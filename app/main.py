
# [START imports]
import os
import cloudstorage as gcs
import webapp2
from google.appengine.api import images
from settings import SRC_BUCKET, DST_BUCKET, BUCKET_NAME, ALLOW_EXT, ROWS, COLS
# [END imports]


# [START retries]
gcs.set_default_retry_params(
    gcs.RetryParams(initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15))
# [END retries]


class MainPage(webapp2.RequestHandler):
    """Main page for GCS demo application."""

    page_size = 100

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(
            'Chop Cutting GCS Application running from Version: {}\n'.format(os.environ['CURRENT_VERSION_ID']))
        self.response.write('Using bucket name: {}\n\n'.format(BUCKET_NAME))
        self.response.write('\n\n')

        self.response.write('Listing files...{} \n'.format(SRC_BUCKET))
        tmp_paths = self.list_bucket(bucket=SRC_BUCKET)
        self.response.write('\n\n')

        self.response.write('Chop cutting...\n')
        for filepath in tmp_paths:
            if os.path.splitext(filepath)[1].lower() in ALLOW_EXT:
                self.response.write('\t{}\n'.format(filepath))
                if not self.exist_file(filepath=filepath):
                    self.response.write('\t\tNo exist\n')
                else:
                    self.response.write('\t\tChop Cutting\n'.format(filepath))
                    # cnt = self.chop_cut(filepath=filepath)
                    # self.response.write('\t\t# amount of sub files: {}\n'.format(len(cnt)))
        self.response.write('\n\n')

        # self.response.write('Deleting files...\n')
        # self.delete_files(filepaths=tmp_paths)
        # self.response.write('\n\n')

        self.response.write('\n\nThe demo ran successfully!\n')

    # [START check exist]
    @staticmethod
    def exist_file(filepath):
        try:
            gcs.stat(filepath)
            return True
        except gcs.NotFoundError as e:
            print e
            return False
    # [END check exist]

    # [START list_bucket]
    def list_bucket(self, bucket):
        filepaths = []
        for stat in gcs.listbucket(bucket, delimiter="/", max_keys=self.page_size):
            try:
                fname = stat.filename
                if not stat.is_dir and os.path.splitext(fname)[1].lower() in ALLOW_EXT:
                    filepaths.append(fname)
                    self.response.write('\t {}\n'.format(fname))
            except Exception as e:
                self.response.write('\t {}\n'.format(str(e)))
                continue
        return filepaths
    # [END list_bucket]

    # [START delete_files]
    def delete_files(self, filepaths):
        for filepath in filepaths:
            self.response.write('  Delete file {}\n'.format(filepath))
            try:
                gcs.delete(filepath)
            except gcs.NotFoundError:
                pass
    # [END delete_files]

    def chop_cut(self, filepath):
        cnt = 0
        try:
            img = images.Image(filename=filepath)
            base_name = filepath.split('/')[-1]
            base, ext = os.path.splitext(base_name)

            h, w = float(img.height), float(img.width)
            thumb_h, thumb_w = int(h / ROWS), int(w / COLS)
            for j in range(ROWS):
                for i in range(COLS):
                    y1 = max(0.0, j * thumb_h) / h
                    y2 = min(h, (j + 1.0) * thumb_h - 1.0) / h
                    x1 = max(0.0, i * thumb_w) / w
                    x2 = min(w, (i + 1.0) * thumb_w - 1.0) / w

                    dst_file_path = DST_BUCKET + "{}_{}_{}{}".format(base, j, i, ext)
                    img.crop(left_x=x1, top_y=y1, right_x=x2, bottom_y=y2)
                    images.get_serving_url(blob_key=None, size=None, crop=False, secure_url=None,
                                           filename=dst_file_path, rpc=None)
                    cnt += 1
        except Exception as e:
            self.response.write('  exception {}\n'.format(str(e)))
        return cnt


app = webapp2.WSGIApplication(
    [('/', MainPage)], debug=True)
# [END sample]
