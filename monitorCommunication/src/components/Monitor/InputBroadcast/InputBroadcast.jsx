import { Box, Button, Flex, Input, InputGroup, InputRightElement } from "@chakra-ui/react";
import { useContext, useState } from "react";
import { WebSocketContext } from "../../../context/socket";

const InputBroadcast = () => {

    const contextValues = useContext(WebSocketContext)
    const {socket} = contextValues.socketContext

    const [inputMessage, setInputMessage] = useState('')

    const handleSendBroadcast= () => {
        if(inputMessage.trim() === ''){
            return
        }
        socket.emit(`broadcast`, {from:'monitor', msg:inputMessage})
        setInputMessage('')
    }

    const handleMessageInput = ({target}) => {
        const {value} = target
        setInputMessage(value)
    }

    return ( 
        <InputGroup size="md" width="50%" margin={'0 10px'} justifyContent="center">
            <Input
            pr='4.5rem'
            type='text'
            value={inputMessage}
            onChange={handleMessageInput}
            placeholder='Broadcast'
            onKeyPress={(e) => {
                if (e.key === 'Enter') {
                    handleSendBroadcast()
                }
            }}
         />
                <InputRightElement width='4.5rem'>
                <Button h='1.75rem' size='sm' onClick={handleSendBroadcast} disabled={inputMessage.trim() ===''}>
                    Send
                </Button>
            </InputRightElement>
        </InputGroup>
        );
    }
    
    export default InputBroadcast;