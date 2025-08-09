# Nintendo Switch 2 JoyCon as Mouse

Software to use your joy-con 2 on Mac as mouse. I intend to make it a fully customizable software, but for now, all you can do is connect a right joy con and use it as a mouse

# How to use this?

I intend to make an easy app where end-users can just open the app and have an easy time configuring buttons, sensitivity and such. But for now, you can just run the python app

1. Create a virtual enviroment
2. Install requirements from requirements.txt
3. Run main.py
4. Press the sync button on your right joy con
5. Enjoy your mouse

It's not the best mouse ever, but it's still fun to be able to use it like that

---
## Special Thanks! 
I was only able to do this because of [the original joycon2py by  TheFrano](https://github.com/TheFrano/joycon2py/)

Some more info I used was provided in [german77's joycon driver](https://github.com/german77/JoyconDriver)


# Building
macOS: setup.py py2app     
Windows: pyinstaller --add-data "./assets/*.png:assets/." .\main.py 