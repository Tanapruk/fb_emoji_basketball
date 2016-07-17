# Facebook emoji Basketball Script

Python shell script to automate playing Facebook basketball. It is a script that use uiautomator python
[![Facebook Basketball Shooter](http://i.giphy.com/AC9OHzx1RrEpW.gif)](http://www.youtube.com/watch?v=DkmA7ZoSWr4)

####Requirement
* Android phone with root access
* PC (Mac or Linux are preferable)
* ADB
* Python
* [uiautomator](https://github.com/xiaocong/uiautomator)

####Instruction
* Plug your Android device to your PC and connect to ADB
* Launch the basketball game
* Run the script (Required python, uiautomate and adb)
* Enjoy

#### Level Support
* score 1-10 (100%)
* score 11-20 (100%)
* score 21-30 (98%)
* score 31-40 (90%)
* score 41-50 (70%)
* in progress..

#### Explanation
* score 1-10 The rim is stationary. We can simply use drag function from the ball to the rim.
* score 11-20 The rim is moving and has a constant speed. Releasing the ball and set shooting location as an offset of the releasing position by constant pixels.
* score 21-30 The moving rim speed is quicker than the score 11-20 and has an unstable speed. We cannot use the method in the previous level. By trial and error, I found that we should fix the shooting position to the middle of the screen. The decision making will be made in the releasing position. However, the optimal releasing position is so small, so the ball get shot not very often. I counter this problem by adding a delay when the rim moves to area before the optimal releasing position.
* score 31-40 The rim is moving around across two axis in a transparent container. By statistic, it move to the middle of the screen very often, so I fixed the shooting position to the frequent passing position. The logic is similar to the score 21-30.
* score 41-50 Similar to the score 31-40, but with bigger boundary. The logic is being developed. Initial guess is like the previous 3 sections.

### Support Devices
* I only test in my Nexus 4, but it should be fine on other devices.
