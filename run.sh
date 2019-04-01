# APP 运行环境

#APP_ENVIRON = 'dev'
#APP_AREA = 'all'


APP_ENVIRON = '$1'
APP_AREA = '$2'
BASE_DIR = $(cd ‘dirname $0‘; pwd)
APP_PROXY = "$BASE_DIR/app_proxy.py"

mkdir -p $BASE_DIR/logs
python3 $APP_PROXY "$APP_ENVIRON" "$APP_AREA" >> $BASE_DIR/logs/run.sh 2>&1 &

exit 0