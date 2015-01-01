import zipfile
from google.appengine.api import app_identity
import io
import cloudstorage as gcs
import mimetypes
import os


def store_file_in_gcs(log, name, content):
    default_bucket = app_identity.get_default_gcs_bucket_name()

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    key_name = "/%s/%s/%s_%s/%s" % (default_bucket, log.application_name, log.created_at.isoformat(), log.salt, name)
    mimetypes_files = os.path.join(os.path.dirname(__file__), "../mime.types")
    mimetypes.init([mimetypes_files])
    content_type, _ = mimetypes.guess_type(key_name)
    with gcs.open(key_name, "w", content_type=content_type, options={"x-goog-acl": "public-read"}, retry_params=write_retry_params) as gcs_file:
        gcs_file.write(content)

    return key_name


def enum_request_files(log, file_infos):
    for file_info in file_infos:
        gsc_object_name = file_info.gs_object_name[3:]
        with gcs.open(gsc_object_name) as gs_file:  # remove the /gs prefix
            if file_info.filename.endswith(".zip"):
                z = zipfile.ZipFile(gs_file)
                for filename in z.namelist():
                    yield store_file_in_gcs(log, filename, z.read(filename))
            else:
                yield file_info.filename


def enum_message_files(log, message):
    def enum_name_content():
        for name, content in getattr(message, "attachments", []):
            if name.endswith(".zip"):
                with io.BytesIO(content.decode()) as zip_file_data:
                    z = zipfile.ZipFile(zip_file_data)
                    for filename in z.namelist():
                        yield filename, z.read(filename)
            else:
                yield name, content.decode()

    for filename, data in enum_name_content():
        link = store_file_in_gcs(log, filename, data)
        yield link

