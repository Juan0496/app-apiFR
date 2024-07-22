import pyrebase
firebaseConfig = {
  "apiKey": "AIzaSyAxV11L0b_o1bbJclwBIZRtjywxoTm-9_Y",
  "authDomain": "homesecurity-f0dd6.firebaseapp.com",
  "projectId": "homesecurity-f0dd6",
  "storageBucket": "homesecurity-f0dd6.appspot.com",
  "messagingSenderId": "225800710622",
  "appId": "1:225800710622:web:6a4653300c213847cd554f",
 " measurementId": "G-CW4WDP8QSC",
 'databaseURL':""
}
firebase=pyrebase.initialize_app(firebaseConfig)
autho = firebase.auth()