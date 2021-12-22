coverage run --source=./src -m pytest test/
mkdir -p coverage_report
coverage html -d coverage_report
google-chrome coverage_report/index.html