#GPLv3 Raif Sarcich 2011

import random
import datetime
from pieobject import PieObject

ipsum = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Nulla vel mauris sapien, ut porttitor nisi.",
    "Curabitur in diam at diam porttitor suscipit.",
    "In condimentum elit sit amet dui tempor accumsan.",
    "Ut sit amet quam eros, vitae venenatis lectus.",
    "Nunc auctor orci dui, vel imperdiet nibh.",
    "Fusce a metus sit amet odio semper tempor.",
    "Ut consectetur nulla ut magna varius lacinia.",
    "Vestibulum tincidunt elit quis elit gravida vel posuere arcu tincidunt.",
    "Donec faucibus vestibulum eros, ac rutrum elit sodales blandit.",
    "Morbi dignissim quam a odio eleifend aliquet.",
    "Maecenas a nisi nibh, ac convallis turpis.",
    "Nam at nisi mattis velit laoreet scelerisque.",
    "Cras pulvinar quam sit amet urna fringilla fringilla.",
    "Vestibulum in felis in nisi cursus mattis id at libero.",
    "Donec vel ligula quis massa rutrum suscipit.",
    "In placerat ipsum eget odio dapibus vehicula.")

namelist = (
    "Chanel Hellman",
    "Vaughn Arakaki",
    "Serena Haman",
    "Millie Metzler",
    "Maira Railsback",
    "Ozie Hilger",
    "Nathaniel Gault",
    "Ivonne Galgano",
    "Taryn Delosreyes",
    "Yan Jerkins",
    "Elmer Boydston",
    "Agripina Botts",
    "Reuben Maddux",
    "Reatha Stansell",
    "Deloise Hillyard",
    "Celia Crocket",
    "Maurita Swick",
    "Phung Maddix",
    "Yesenia Lieb",
    "Hubert Courser")

urllist = (
    "http://www.asdf.com/=?ueeeue",
    "https://conan.org/phoebe.html",
    "www.jones.net",
    "http://pu.er/2n34t",
    "http://www3.jesus.loves.uu/worship.php"
    )

filenamelist = ('basin.pdf', 'sink.pdf', 'bath.pdf', 'shower.pdf', 'loo.pdf')

rootlist = ('library', 'projects', 'staging_web', 'staging_desktop')

def spoof_pieobject(objtype="normal"):
    if objtype == 'normal':
        t = random.choice(ipsum)
        a = random.choice(namelist)
        d = datetime.datetime.today()
        ro = PieObject(t, a, d)
        ro.FileData_FileName = random.choice(filenamelist)
        ro.FileData_Root = random.choice(rootlist)
    if objtype == 'web':
        ro = PieObject()
        ro.WebData_Url = random.choice(urllist)
        ro.WebData_PageUrl = ro.WebData_Url
        ro.WebData_LinkText = random.choice(ipsum)
    ro.MakeBibData()
    ro.add_tag('Test')
    return ro


