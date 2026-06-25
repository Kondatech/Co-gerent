@echo off
echo Building Tailwind CSS...
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
echo Done!