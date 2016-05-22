#! /usr/bin/env bash
# 2016, Moritz Kaspar Rudert (mortzu) <post@moritzrudert.de>.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of
#   conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this list
#   of conditions and the following disclaimer in the documentation and/or other materials
#   provided with the distribution.
#
# * The names of its contributors may not be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# * Feel free to send Club Mate to support the work.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS
# AND CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Set path to defaults
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Get last port from configuration files
VNC_PORT="$(cat /var/lib/anastasia/*/vncport | sort -n | tail -n1)"

# If returned port is empty
# start at 5900
if [ -z "$VNC_PORT" ]; then
  VNC_PORT=5900
fi

# Iterate over all containers
for CONTAINER_NAME in $(lxc-ls -1); do
  # Check if directory already exists
  if [ ! -d "/var/lib/anastasia/${CONTAINER_NAME}" ]; then
    mkdir -p "/var/lib/anastasia/${CONTAINER_NAME}"
  fi

  # If no password for VNC is defined
  # generate a new one
  if [ ! -f "/var/lib/anastasia/${CONTAINER_NAME}/vncpasswd" ]; then
    echo "$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)" > "/var/lib/anastasia/${CONTAINER_NAME}/vncpasswd"
  fi

  # If no VNC port is defined
  # calculate a new one
  if [ ! -f "/var/lib/anastasia/${CONTAINER_NAME}/vncport" ]; then
    VNC_PORT=$(($VNC_PORT+1))

    echo "$VNC_PORT" > "/var/lib/anastasia/${CONTAINER_NAME}/vncport"
  fi

  # Get defined values
  VNC_PORT="$(</var/lib/anastasia/${CONTAINER_NAME}/vncport)"
  VNC_PASSWD="$(</var/lib/anastasia/${CONTAINER_NAME}/vncpasswd)"

  # Replace placeholder in systemd service
  # and install systemd
  sed -e "s/___VNCPASSWD___/${VNC_PASSWD}/g" \
      -e "s/___VNCPORT___/${VNC_PORT}/g" \
      -e "s/___CONTAINER_NAME___/${CONTAINER_NAME}/g" \
      /opt/anastasia-api/systemd/vnclxc.service.template > \
      /etc/systemd/system/vnclxc-${VNC_PORT}.service

  # Reload systemd
  systemctl daemon-reload

  # Enable new service
  systemctl enable vnclxc-${VNC_PORT}.service
done
