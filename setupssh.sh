git config --global user.name "Graydon Strachan"
git config --global user.email "glstrachan@outlook.com"
git remote set-url origin git@github.com:glstrachan/aiweather.git
ssh-keygen -t ed25519 -C "glstrachan@outlook.com"
eval `ssh-agent -s`
ssh-add ~/.ssh/id_ed25519
vim ~/.ssh/id_ed25519.pub