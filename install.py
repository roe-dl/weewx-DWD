# installer DWD
# Copyright 2023 Johanna Roedenbeck
# Distributed under the terms of the GNU Public License (GPLv3)

# Caution! Not finished.

"""
    This script is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This script is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
"""

from weecfg.extension import ExtensionInstaller
import os
import os.path
import stat
import shutil

def loader():
    return DWDInstaller()

class DWDInstaller(ExtensionInstaller):
    def __init__(self):
        super(DWDInstaller, self).__init__(
            version="0.x",
            name='weatherforecasts',
            description='Service to retrieve data from weather services',
            author="Johanna Roedenbeck",
            author_email="",
            data_services='user.weatherservices.DWDservice',
            config={
                'StdWXCalculate': {
                    'Calculations': {
                        'barometerDWD':'software, loop'
                    }
                },
                'DeutscherWetterdienst': {
                },
                'WeatherServices': {
                    'path': '/etc/weewx/skins/Belchertown/dwd',
                    'current': {
                        'safe':'True'
                    },
                    'forecast': {
                        'icons':'replace_me',
                        'orientation':'h,v',
                        '#show_obs_symbols':'True',
                        '#show_obs_description':'True',
                        '#show_placemark':'True'
                    },
                    'warning': {
                        'icons':'replace_me'
                    },
                    'Belchertown': {
                        'section':'Belchertown',
                        'warnings':'replace_me',
                        'forecast':'replace_me',
                        '#include_advance_warings':'0',
                        '#aqi_source':'replace_me',
                        '#compass_lang':'replace_me'
                    }
                }
            },
            files=[('bin/user', [
                'bin/user/weatherservices.py',
                'bin/user/weatherservicesutil.py',
                'bin/user/weatherservicesdb.py',
                'bin/user/weatherservicesradar.py',
                'bin/user/weathercodes.py',
                'bin/user/wildfire.py',
                'bin/user/capwarnings.py',
                'usr/local/bin/html2ent.ansi',
                'usr/local/bin/wget-dwd']),]
            )
      
    def configure(self, engine):
        # path of the user directory
        print(engine.root_dict)
        user_root = engine.root_dict.get('USER_ROOT',engine.root_dict['USER_DIR'])
        # path for system wide commands
        bin = '/usr/local/bin'
        # links to create and files to copy
        links = ['dwd-cap-warnings','bbk-warnings','msc-warnings']
        cps = ['wget-dwd','html2ent.ansi']
        # complete path of capwarnings.py
        capwarnings_fn = os.path.join(user_root,'capwarnings.py')
        # make capwarnings.py executable
        try:
            engine.logger.log("chmod u=rwx,g=rx,o=rx %s" % capwarnings_fn)
        except AttributeError:
            engine.printer.out("chmod u=rwx,g=rx,o=rx %s" % capwarnings_fn)
        if not engine.dry_run:
            os.chmod(capwarnings_fn,stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
        # create symbolic links 
        for li in links:
            fn = os.path.join(bin,li)
            try:
                engine.logger.log("ln -s %s %s" % (capwarnings_fn,fn))
            except AttributeError:
                engine.printer.out("ln -s %s %s" % (capwarnings_fn,fn))
            if not engine.dry_run:
                os.symlink(capwarnings_fn,fn)
        # copy files
        for cp in cps:
            fni = os.path.join(user_root,'usr','local','bin',cp)
            fno = os.path.join(bin,cp)
            try:
                engine.logger.log("cp %s %s" % (fni,fno))
            except AttributeError:
                engine.printer.out("cp %s %s" % (fni,fno))
            if not engine.dry_run:
                shutil.copy(fni,fno)
            try:
                engine.logger.log("chmod u=rwx,g=rx,o=rx %s" % fno)
            except AttributeError:
                engine.printer.out("chmod u=rwx,g=rx,o=rx %s" % fno)
            if not engine.dry_run:
                os.chmod(fno,stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
        # no change of the configration file
        return False
