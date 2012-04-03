#!/bin/bash

HOST="members.iinet.net.au"
USER="raifsarcich"
PASS="yiblwu7yt"
LCD="~/development/v2Pieberry/website/published"
RCD="/pieberry"
lftp -c "set ftp:list-options -a;
open ftp://$USER:$PASS@$HOST; 
lcd $LCD;
cd $RCD;
mirror --verbose --reverse"

