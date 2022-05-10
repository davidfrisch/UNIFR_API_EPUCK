import { Button, Input, InputGroup, InputRightElement } from "@chakra-ui/react";
import { useContext, useState, useEffect } from "react";
import { WebSocketContext } from "../../../../../context/socket";

const LogSendMessage = ({ dest }) => {
    const { socketContext } = useContext(WebSocketContext);
    const { socket } = socketContext;
    const [inputMessage, setInputMessage] = useState("");
    
    const handleMessageInput = ({ target }) => {
        const { value } = target;
        setInputMessage(value);
    };
    
    const handleSend = () => {
        if(inputMessage.trim() === ""){
            return
        }
        
        socket.emit(`send_msg_to`, { dest: dest, msg: inputMessage });
        setInputMessage("");
    };
    
    return (
        <InputGroup size="md" marginBottom={3}>
        <Input
        pr="4.5rem"
        type="text"
        value={inputMessage}
        onChange={handleMessageInput}
        onKeyPress={(e) => {
            if (e.key === 'Enter') {
                handleSend()
            }
        }}
        />
        <InputRightElement width="4.5rem">
        <Button
        h="1.75rem"
        size="sm"
        onClick={handleSend}
        disabled={inputMessage.trim() === ""}
        
        >
        Send
        </Button>
        </InputRightElement>
        </InputGroup>
        );
    };
    
    export default LogSendMessage;
    