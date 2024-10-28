def split_buffer_to_messages(buffer):
    messages = []
    index = 0

    while index < len(buffer):
        # Look for the start of a new message, assuming it starts with '\x08'
        if buffer[index] == 0x08:
            # If we are not at the start of the buffer, consider everything before as a message
            if index > 0:
                messages.append(current_message)
            
            # Start a new message
            current_message = bytearray()
        
        # Add the current byte to the current message
        current_message.append(buffer[index])
        
        # Move to the next byte
        index += 1
    
    # Append the last collected message
    if current_message:
        messages.append(current_message)
    
    return messages

# Example usage
data = b'\x08\x02\x10\x03\x1a\x06mess1\x08\x02\x10\x03\x1a\x01mess2\x08\x02\x10\x03\x1a\x04mess3'
result = split_buffer_to_messages(data)
print(result)
print([bytes(message) for message in result])