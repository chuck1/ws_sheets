pip freeze > requirements_dev.txt
sed -i 's/git@github.com:/https:\/\/github.com\//' requirements_dev.txt
