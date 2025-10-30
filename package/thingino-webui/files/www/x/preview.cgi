#!/bin/haserl
<%in _common.cgi %>
<%
msg="Camera Preview"
page_title=$msg
which motors > /dev/null && has_motors="true"
%>
<%in _header.cgi %>

<div class="row preview">
<div class="col-lg-1">

<div class="d-flex flex-nowrap flex-lg-wrap align-content-around gap-1" aria-label="controls">
<input type="checkbox" class="btn-check" name="motion" id="motion" value="1">
<label class="btn btn-dark border mb-2" for="motion" title="Motion Guard"><img src="/a/motion.svg" alt="Motion Guard" class="img-fluid"></label>

<input type="checkbox" class="btn-check" name="rotate" id="rotate" value="1">
<label class="btn btn-dark border mb-2" for="rotate" title="Rotate 180°"><img src="/a/rotate.svg" alt="Rotate 180°" class="img-fluid"></label>

<input type="checkbox" class="btn-check" name="gpio_daynight" id="gpio_daynight" value="1">
<label class="btn btn-dark border mb-2" for="gpio_daynight" title="Night mode"><img src="/a/night.svg" alt="Day/Night Mode" class="img-fluid"></label>

<input type="checkbox" class="btn-check" name="image_running_mode" id="image_running_mode" value="0">
<label class="btn btn-dark border mb-2" for="image_running_mode" title="color mode"><img src="/a/color.svg" alt="Color mode" class="img-fluid"></label>

<% if [ -n "$gpio_ircut" ]; then %>
<input type="checkbox" class="btn-check" name="gpio_ircut" id="gpio_ircut" value="1">
<label class="btn btn-dark border mb-2" for="gpio_ircut" title="IR filter"><img src="/a/ircut_filter.svg" alt="IR filter" class="img-fluid"></label>
<% fi %>

<% if [ -n "$gpio_ir850" ]; then %>
<input type="checkbox" class="btn-check" name="gpio_ir850" id="gpio_ir850" value="1">
<label class="btn btn-dark border mb-2" for="gpio_ir850" title="IR LED 850 nm"><img src="/a/light_850nm.svg" alt="850nm LED" class="img-fluid"></label>
<% fi %>

<% if [ -n "$gpio_sensor_switch" ]; then %>
<input type="checkbox" class="btn-check" name="gpio_sensor_switch" id="gpio_sensor_switch" value="1">
<label class="btn btn-dark border mb-2" for="gpio_sensor_switch" title="CAM Select"><img src="/a/cam_select.svg" alt="CAM Select" class="img-fluid"></label>
<% fi %>

<% if [ -n "$gpio_ir940_x" ]; then %>
<input type="checkbox" class="btn-check" name="gpio_ir940" id="gpio_ir940" value="1"> 
<label class="btn btn-dark border mb-2" for="gpio_ir940" title="CAM Select"><img src="/a/light_940nm.svg" alt="CAM Select" class="img-fluid"></label> 
<% fi %>

<% if [ -n "$gpio_white" ]; then %>
<input type="checkbox" class="btn-check" name="gpio_white" id="gpio_white" value="1">
<label class="btn btn-dark border mb-2" for="gpio_white" title="White LED"><img src="/a/light_white.svg" alt="White light" class="img-fluid"></label>
<% fi %>

<button type="button" class="btn btn-dark border mb-2" title="Zoom" data-bs-toggle="modal" data-bs-target="#mdPreview">
<img src="/a/zoom.svg" alt="Zoom" class="img-fluid"></button>
</div>

</div>
<div class="col-lg-10">
<div id="frame" class="position-relative mb-2">
<img id="preview" src="/a/nostream.webp" class="img-fluid" alt="Image: Preview">
<% if [ "true" = "$has_motors" ]; then %><%in _motors.cgi %><% fi %>
</div>

<% if [ "true" = "$has_motors" ]; then %>
<p class="small">Move mouse cursor over the center of the preview image to reveal the motor controls.
Use a single click for precise positioning, double click for coarse, larger distance movement.</p>
<% fi %>

<div class="alert alert-secondary">
<p class="mb-0"><img src="/a/mute.svg" alt="Icon: No Audio" class="float-start me-2" style="height:1.75rem" title="No Audio">
lease note, there is no audio on this page. Open the RTSP stream in a player to hear audio.</p>
<b id="playrtsp" class="cb"></b>
</div>
</div>

<div class="col-lg-1">
<div class="d-flex flex-nowrap flex-lg-wrap align-content-around gap-1" aria-label="controls">
<a href="image.cgi" target="_blank" class="btn btn-dark border mb-2" title="Save image"><img src="/a/download.svg" alt="Save image" class="img-fluid"></a>
<button type="button" class="btn btn-dark border mb-2" title="Send to email" data-sendto="email"><img src="/a/email.svg" alt="Email" class="img-fluid"></button>
<button type="button" class="btn btn-dark border mb-2" title="Send to Telegram" data-sendto="telegram"><img src="/a/telegram.svg" alt="Telegram" class="img-fluid"></button>
<button type="button" class="btn btn-dark border mb-2" title="Send to FTP" data-sendto="ftp"><img src="/a/ftp.svg" alt="FTP" class="img-fluid"></button>
<button type="button" class="btn btn-dark border mb-2" title="Send to MQTT" data-sendto="mqtt"><img src="/a/mqtt.svg" alt="MQTT" class="img-fluid"></button>
<button type="button" class="btn btn-dark border mb-2" title="Send to Webhook" data-sendto="webhook"><img src="/a/webhook.svg" alt="Webhook" class="img-fluid"></button>
<button type="button" class="btn btn-bark border mb-2" title="Yandex Disk" data-sendto="yadisk"><img src="/a/yadisk.svg" alt="Yandex Disk" class="img-fluid"></button>
</div>
</div>

</div>

<%in _preview.cgi %>

<script>
<%
for i in email ftp mqtt telegram webhook yadisk; do
	continue
#	[ "true" = $(eval echo \$${i}_enabled) ] && continue
%>
{
	let a = document.createElement('a')
	a.href = 'tool-send2<%= $i %>.cgi'
	a.classList.add('btn','btn-outline-danger','mb-2')
	a.title = 'Configure sent2<%= $i%> plugin'
	a.append($('button[data-sendto=<%= $i %>] img'))
	$('button[data-sendto=<%= $i %>]').replaceWith(a);
}
<% done %>

const preview = $("#preview");
preview.onload = function() { URL.revokeObjectURL(this.src) }

const ImageBlackMode = 1
const ImageColorMode = 0

function updatePreview(data) {
	const blob = new Blob([data], {type: 'image/jpeg'});
	const url = URL.createObjectURL(blob);
	preview.src = url;
	$("#preview_fullsize").src = url;
	ws.send('{"action":{"capture":null}}');
}

const wsPort = location.protocol === "https:" ? 8090 : 8089;
let ws = new WebSocket(`//${document.location.hostname}:${wsPort}?token=<%= $ws_token %>`);

const gpio_params = ['ir850', 'ir940', 'white', 'ircut', 'sensor_switch', 'daynight'];
const image_params = ['running_mode'];

ws.onopen = () => {
	console.log('WebSocket connection opened');
	ws.binaryType = 'arraybuffer';
	const payload = '{'+
		'"image":{"hflip":null,"vflip":null},'+
		'"image":{"running_mode":null},'+
		'"gpio":{"ir850":null,"ircut":null,"white":null,"daynight":null,"sensor_switch":null},'+
		'"motion":{"enabled":null},'+
		'"rtsp":{"username":null,"password":null,"port":null},'+
		'"stream0":{"rtsp_endpoint":null},'+
		'"action":{"capture":null}'+
		'}'
	console.log(ts(), '===>', payload);
	ws.send(payload);
}
ws.onclose = () => {
	console.log('WebSocket connection closed');
	ws = null;
}
ws.onerror = (err) => {
	console.error('WebSocket error', err);
	ws.close();
}
ws.onmessage = (ev) => {
	let data;

	if (typeof ev.data == 'string') {
		if (ev.data == '') {
			console.log('Empty response');
			return;
		}
		if (ev.data == '{"action":{"capture":"initiated"}}') {
			return;
		}
		console.log(ts(), '<===', ev.data);
		const msg = JSON.parse(ev.data);

		if (msg.image) {
                        data = msg.image;
			if (msg.image.hflip) {
				$('#rotate').checked = msg.image.hflip;
			}
			if (msg.image.vflip) {
				$('#rotate').checked = msg.image.vflip;
			}
                        if (msg.image.running_mode <= 1) {
                        	$('#image_running_mode').checked = (msg.image.running_mode == 0);
                        }
		}
		if (msg.gpio) {
                        data = msg.gpio;
                        if (data) {
                                gpio_params.forEach((x) => {
                                        if (typeof(data[x]) !== 'undefined')
						 $(`#gpio_${x}`).checked = (data[x] == 1);
                                });
                        }
		}
		if (msg.motion) {
			if (msg.motion.enabled) $('#motion').checked = msg.motion.enabled;
		}
		if (msg.rtsp) {
			const r = msg.rtsp;
			if (r.username && r.password && r.port)
				$('#playrtsp').innerHTML = `mpv rtsp://${r.username}:${r.password}@${document.location.hostname}:${r.port}/${msg.stream0.rtsp_endpoint}`;
		}
	} else if (ev.data instanceof ArrayBuffer) {
		updatePreview(ev.data);
	}
}

function sendToWs(payload) {
	payload = payload.replace(/}$/, ',"action":{"save_config":null}}')
	console.log(ts(), '===>', payload);
	ws.send(payload);
}

function saveValue(domain, name) {
        const el = $(`#${domain}_${name}`);
        if (!el) {
                // console.error(`Element #${domain}_${name} not found`);
                return;
        }

        let value;
        if (el.type == "checkbox") {
                if (domain == 'image' && name == 'running_mode')
                        value = el.checked ? 0 : 1;
                else
                        value = el.checked;
        }

        let payload = `"${name}":${value}`
        sendToWs('{"'+domain+'":{'+payload+'}}');
}

async function toggleDayNight(state) {
	console.log('DayNight change requested`');
	// GPIO
	const ir850_v = ( ($('#gpio_ir850')) ? (state ? true : false) : null);
        let g_payload = `"ir850":${ir850_v}` 
	const ir940_v = ( ($('#gpio_ir940')) ? (state ? true : false) : null);
        //g_payload = `"ir940":${ir940_v},`+g_payload+`` 
	const white_v = ( ($('#gpio_white')) ? (state ? true : false) : null);
        g_payload = `"white":${white_v},`+g_payload+``
	const ircut_v = ( ($('#gpio_ircut')) ? (state ? false : true) : null);
        g_payload = `"ircut":${ircut_v},`+g_payload+`` 
	const daynight_v = ( ($('#gpio_daynight')) ? (state ? true : false) : null);
        g_payload = `"daynight":${daynight_v},`+g_payload+`` 

	// IMAGE
	const running_mode_v = ( ($('#image_running_mode')) ? (state ? 1 : 0) : null);
        let i_payload = `"running_mode":${running_mode_v}` 

	let payload = `{"image":{`+i_payload+`},"gpio":{`+g_payload+`}`

	console.log(ts(), '===>', payload);
	sendToWs(payload);
}

image_params.forEach((x) => {
        const el = $(`#image_${x}`);
        if (!el) {
                console.debug(`element #image_${x} not found`);
                return;
        }
        el.addEventListener('click', (_) => {
                saveValue('image', x);
        });
});

gpio_params.forEach((x) => {
        const el = $(`#gpio_${x}`);
        if (!el) {
                console.debug(`element #gpio_${x} not found`);
                return;
        }
        el.addEventListener('click', (_) => {
                saveValue('gpio', x);
        });
});

$("#motion").addEventListener('change', ev => sendToWs('{"motion":{"enabled":' + ev.target.checked + '}}'));
$('#rotate').addEventListener('change', ev => sendToWs('{"image":{"hflip":' + ev.target.checked + ',"vflip":' + ev.target.checked + '}}'));
$("#gpio_daynight").addEventListener('change', ev => ev.target.checked ? toggleDayNight(true) : toggleDayNight(false));

toggleDayNight();
</script>

<div class="alert alert-dark ui-debug d-none">
<h4 class="mb-3">Debug info</h4>
</div>

<%in _footer.cgi %>
