
# [START imports]
import os
import cloudstorage as gcs
import webapp2
# from google.appengine.api import images
from PIL import Image
import io


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
        try:
            # [header of response]
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('\t\t\tChop Cutting Google AppEngine Application\n')
            self.response.write('=' * 50 + '\n')
            self.response.write('\n\n')

            self.response.write(' Version:    {}\n'.format(os.environ['CURRENT_VERSION_ID']))
            self.response.write(' BucketName: {}\n'.format(BUCKET_NAME))
            self.response.write('       source bucket: {}\n'.format(SRC_BUCKET))
            self.response.write('       result bucket: {}\n'.format(DST_BUCKET))
            self.response.write('\n\n')

            # []
            self.response.write('scanning source bucket ...\n')
            tmp_paths = self.list_bucket(bucket=SRC_BUCKET)
            self.response.write('\n\n')

            self.response.write('chop cutting progress...\n')
            for filepath in tmp_paths:
                if os.path.splitext(filepath)[1].lower() in ALLOW_EXT:
                    self.response.write('  file: {}\n'.format(filepath))
                    cnt = self.chop_cut(filepath=filepath)
                    self.response.write('  # amount of thumb files: {}\n'.format(cnt))
            self.response.write('\n\n')

            # self.response.write('deleting temp files...\n')
            # self.delete_files(filepaths=tmp_paths)
            # self.response.write('\n\n')

            self.response.write('\n\nThe demo ran successfully!\n')
        except Exception as e:
            self.response.write('{}\n'.format(str(e)))

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
                    self.response.write('  {}\n'.format(fname))
            except Exception as e:
                self.response.write('  {}\n'.format(str(e)))
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
        if not self.exist_file(filepath=filepath):
            self.response.write('    no exist\n')
        else:
            self.response.write('    chop cutting\n')
            self.response.write('\tread file: \n')
            contents = self.read_file(filepath)
            pil_img = Image.open(io.BytesIO(contents))
            h, w = pil_img.size
            self.response.write('\t  height: {}, width: {}\n'.format(h, w))
            thumb_h, thumb_w = int(h / ROWS), int(w / COLS)
            self.response.write('\t  thumb_height: {} , thumb_width: {}\n'.format(thumb_h, thumb_w))

            base_name = filepath.split('/')[-1]
            base, ext = os.path.splitext(base_name)

            for j in range(ROWS):
                for i in range(COLS):
                    y1 = max(0, j * thumb_h)
                    y2 = min(h, (j + 1) * thumb_h - 1)
                    x1 = max(0, i * thumb_w)
                    x2 = min(w, (i + 1) * thumb_w - 1)

                    pil_thumb_img = pil_img.crop(box=(x1, y1, x2, y2))
                    _h, _w = pil_thumb_img.size
                    self.response.write('\t  ({}, {}) : {} x {}\n'.format(i, j, _h, _w))

                    byte_io = io.BytesIO()
                    if ext.find('png') != -1:
                        pil_thumb_img.save(byte_io, 'PNG')
                        ext = '.png'
                    else:
                        pil_thumb_img.save(byte_io, 'JPG')
                        ext = '.jpg'

                    fname = "{}_{}_{}{}".format(base, i, j, ext)
                    # self.response.write('\t  thumbnail file: {}\n'.format(fname))
                    self.write_file(fname, byte_io.getvalue())

                    cnt += 1
        return cnt

    @staticmethod
    def read_file(filepath):
        gcs_file = gcs.open(filepath)
        contents = gcs_file.read()
        gcs_file.close()

        return contents

    def write_file(self, fname, contents):
        filepath = DST_BUCKET + fname
        if self.exist_file(filepath):
            self.response.write('\t  already exist {}\n'.format(filepath))
        else:
            self.response.write('\t  write file {}\n'.format(filepath))

            write_retry_params = gcs.RetryParams(backoff_factor=1.1)
            gcs_file = gcs.open(filepath, 'w',
                                content_type='text/plain',
                                retry_params=write_retry_params)
            gcs_file.write(contents)
            gcs_file.close()


app = webapp2.WSGIApplication(
    [('/', MainPage)], debug=True)
# [END sample]
