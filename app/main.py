
# [START imports]
import os
import cloudstorage
import webapp2
from google.appengine.api import images
from google.appengine.ext import ndb

# [END imports]

# [START retries]
cloudstorage.set_default_retry_params(
    cloudstorage.RetryParams(
        initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15
        ))
# [END retries]


class Photo(ndb.Model):
    title = ndb.StringProperty()
    full_size_image = ndb.BlobProperty()


class MainPage(webapp2.RequestHandler):
    """Main page for GCS demo application."""

    def get(self):

        # [START get_default_bucket]
        # bucket_name = os.environ.get(
        #     'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket_name = 'tribalism-emoji-project'
        folder_name = 'data'

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(
            'Demo GCS Application running from Version: {}\n'.format(
                os.environ['CURRENT_VERSION_ID']))
        self.response.write('Using bucket name: {}\n\n'.format(bucket_name))
        # [END get_default_bucket]

        self.tmp_filenames_to_clean_up = []

        bucket = "/{}/{}/".format(bucket_name, folder_name)
        filename = "/{}/{}/{}".format(bucket_name, folder_name, 'demo-test')
        '/tribalism-emoji-project/data/demo-test'

        self.create_file(filename)
        self.response.write('\n\n')

        self.stat_file(filename)
        self.response.write('\n\n')

        filename = "/{}/{}/{}".format(bucket_name, folder_name, 'sample.png')
        self.stat_file(filename)
        self.response.write('\n\n')

        self.list_bucket(bucket)
        self.response.write('\n\n')

        self.response.write('\n\nThe demo ran successfully!\n')

    # [START write]
    def create_file(self, filename):
        """Create a file."""

        self.response.write('Creating file {}\n'.format(filename))

        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        with cloudstorage.open(
            filename, 'w', content_type='text/plain', options={
                'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as cloudstorage_file:
                    cloudstorage_file.write('abcde\n')
                    cloudstorage_file.write('f'*1024*4 + '\n')
        self.tmp_filenames_to_clean_up.append(filename)
    # [END write]

    # [START read]
    def read_file(self, filename):
        self.response.write(
            'Abbreviated file content (first line and last 1K):\n')

        with cloudstorage.open(filename) as cloudstorage_file:
            self.response.write(cloudstorage_file.readline())
            cloudstorage_file.seek(-1024, os.SEEK_END)
            self.response.write(cloudstorage_file.read())
    # [END read]

    def stat_file(self, filename):
        self.response.write('File stat:\n')

        stat = cloudstorage.stat(filename)
        self.response.write(repr(stat))

    def create_files_for_list_bucket(self, bucket):
        self.response.write('Creating more files for listbucket...\n')
        filenames = [bucket + n for n in [
            '/foo1', '/foo2', '/bar', '/bar/1', '/bar/2', '/boo/']]
        for f in filenames:
            self.create_file(f)

    # [START list_bucket]
    def list_bucket(self, bucket):
        """Create several files and paginate through them."""

        self.response.write('Listbucket result:\n')

        # Production apps should set page_size to a practical value.
        page_size = 1
        stats = cloudstorage.listbucket(bucket + '/foo', max_keys=page_size)
        while True:
            count = 0
            for stat in stats:
                count += 1
                self.response.write(repr(stat))
                self.response.write('\n')

            if count != page_size or count == 0:
                break
            stats = cloudstorage.listbucket(
                bucket + '/foo', max_keys=page_size, marker=stat.filename)
    # [END list_bucket]

    def list_bucket_directory_mode(self, bucket):
        self.response.write('Listbucket directory mode result:\n')
        for stat in cloudstorage.listbucket(bucket + '/b', delimiter='/'):
            self.response.write(stat)
            self.response.write('\n')
            if stat.is_dir:
                for subdir_file in cloudstorage.listbucket(
                        stat.filename, delimiter='/'):
                    self.response.write('  {}'.format(subdir_file))
                    self.response.write('\n')

    # [START delete_files]
    def delete_files(self):
        self.response.write('Deleting files...\n')
        for filename in self.tmp_filenames_to_clean_up:
            self.response.write('Deleting file {}\n'.format(filename))
            try:
                cloudstorage.delete(filename)
            except cloudstorage.NotFoundError:
                pass
    # [END delete_files]


app = webapp2.WSGIApplication(
    [('/', MainPage)], debug=True)
# [END sample]
