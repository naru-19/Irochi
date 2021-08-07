pip freeze > requirements.txt
git add .
git commit -m"release"
git push heroku master
git push origin master
