#Sukuinote :D

import time
from datetime import timedelta

# https://stackoverflow.com/a/49361727
def format_bytes(size):
	size = int(size)
	power = 1024
	n = 0
	power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
	while size > power:
		size /= power
		n += 1
	return f"{size:.2f} {power_labels[n]+'B'}"

# https://stackoverflow.com/a/34325723
def return_progress_string(current, total):
	filled_length = int(30 * current // total)
	return '[' + '=' * filled_length + ' ' * (30 - filled_length) + ']'

# https://stackoverflow.com/a/852718
# https://stackoverflow.com/a/775095
def calculate_eta(current, total, start_time):
	if not current:
		return '00:00:00'
	end_time = time.time()
	elapsed_time = end_time - start_time
	seconds = (elapsed_time * (total / current)) - elapsed_time
	thing = ''.join(str(timedelta(seconds=seconds)).split('.')[:-1]).split(', ')
	thing[-1] = thing[-1].rjust(8, '0')
	return ', '.join(thing)

progress_callback_data = dict()
async def progress_callback(current, total, reply, text, upload):
    
	message_identifier = (reply.chat.id, reply.message_id)
	last_edit_time, prevtext, start_time = progress_callback_data.get(message_identifier, (0, None, time.time()))
	if current == total:
		try:
			progress_callback_data.pop(message_identifier)
		except KeyError:
			pass
	elif (time.time() - last_edit_time) > 1:
		handle = 'Upload' if upload else 'Download'
		if last_edit_time:
			speed = format_bytes((total - current) / (time.time() - start_time))
		else:
			speed = '0 B'
		text = f'''{text}
<code>{return_progress_string(current, total)}</code>

<b>Total Size:</b> {format_bytes(total)}
<b>{handle}ed Size:</b> {format_bytes(current)}
<b>{handle} Speed:</b> {speed}/s
<b>ETA:</b> {calculate_eta(current, total, start_time)}'''
		if prevtext != text:
			await reply.edit_text(text)
			prevtext = text
			last_edit_time = time.time()
			progress_callback_data[message_identifier] = last_edit_time, prevtext, start_time
