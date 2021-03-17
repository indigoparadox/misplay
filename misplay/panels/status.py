
import subprocess
from .panel import TextPanel

class StatusPanel( TextPanel ):

    def update( self, elapsed ):
        cmd = \
            "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        cpu_info = subprocess.check_output( cmd, shell=True ).decode( 'utf-8' )

        cmd = \
            "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        mem_use = subprocess.check_output( cmd, shell=True ).decode( 'utf-8' )

        cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        disk_use = subprocess.check_output( cmd, shell=True ).decode( 'utf-8' )

        self.text( '{} {} {}'.format( cpu_info, mem_use, disk_use ), 0 )
