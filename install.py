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
                'bin/user/weatherserviceshealth.py',
                'bin/user/weathercodes.py',
                'bin/user/wildfire.py',
                'bin/user/capwarnings.py']),]
            )
      
    def configure(self, engine):
        # path of the user directory
        print(engine.root_dict)
        user_root = engine.root_dict.get('USER_ROOT',engine.root_dict.get('USER_DIR'))
        if not user_root:
            print('user directory not found. Create links manually.')
            return False
        # path for system wide commands
        bin = '/usr/local/bin'
        # links to create and files to copy
        links = ['dwd-cap-warnings','bbk-warnings','msc-warnings']
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
                try:
                    os.symlink(capwarnings_fn,fn)
                except OSError as e:
                    try:
                        engine.logger.log("%s %s" % (e.__class__.__name__,e))
                        engine.logger.log("try setting the link by hand")
                    except AttributeError:
                        engine.printer.out("%s %s" % (e.__class__.__name__,e))
                        engine.printer.out("try setting the link by hand")
        # no change of the configration file
        return False
