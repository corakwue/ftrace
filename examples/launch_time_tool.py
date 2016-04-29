#Launch Time for peformance validation
#Author: Hao Wang
#build a dictionary for 10 application

import os
import time
import subprocess

App_List = {'camera':'com.google.android.GoogleCamera/com.android.camera.CameraActivity',
			'chrome':'com.android.chrome/com.google.android.apps.chrome.Main',
			'google_map':'com.google.android.apps.maps/com.google.android.maps.MapsActivity',
			'contacts':'com.google.android.contacts/com.android.contacts.activities.PeopleActivity',
			'settings':'com.android.settings/.Settings',
			'gmail':'com.google.android.gm/.ConversationListActivityGmail',
			'music':'com.google.android.music/com.android.music.activitymanagement.TopLevelActivity',
			'dialer':'com.google.android.dialer/.extensions.GoogleDialtactsActivity',
			'youtube':'com.google.android.youtube',
			'playstore':'com.android.vending/.AssetBrowserActivity'}

Pkg_List = {'camera':'com.google.android.GoogleCamera',
			'chrome':'com.android.chrome',
			'google_map':'com.google.android.apps.maps',
			'contacts':'com.google.android.contacts',
			'settings':'com.android.settings',
			'gmail':'com.google.android.gm',
			'music':'com.google.android.music',
			'dialer':'com.google.android.dialer',
			'youtube':'com.google.android.youtube',
			'playstore':'com.android.vending'}
			
#Access App_List's element
#Loop 10 times, total 100 html file
for i in range(10):
	for key in App_List:
		Launch_Systrace = 'python systrace.py -t 10 -b 10000 gfx idle freq sched input view am wm -o '+key+'_'+str(i)+'.html'
		print Launch_Systrace
		Start_Activity = 'adb shell am start ' + App_List[key]
		subprocess.Popen(Launch_Systrace)
		time.sleep(3)
		os.system(Start_Activity)
		time.sleep(7)
		Stop_Activity = 'adb shell am force-stop ' + Pkg_List[key]
		os.system(Stop_Activity)
		time.sleep(10)