
# settings of bucket
BUCKET_NAME = 'tribalism-emoji-project'

SRC_BUCKET = '/{}/{}/'.format(BUCKET_NAME, 'data')
DST_BUCKET = '/{}/{}/'.format(BUCKET_NAME, 'data/result')

ALLOW_EXT = ['.png', '.jpg', '.bmp', '.jepg']
# chop cutting settings
ROWS = 6
COLS = 5
