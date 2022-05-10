import { Box, Checkbox, Flex, Heading, Input, Stack } from "@chakra-ui/react";
import { useState } from "react";
import LogSendMessage from "./LogsCard/LogSendMessage";
import LogMessages from "./LogsCard/LogMessages"
import AccordionCamera from "./LiveCamera/AccordionCamera";

const Card = ({id, logs}) => {

    const [showReceivedMessage, setShowReceivedMessage] = useState(true)
    const [showSendedMessage, setShowSendedMessage] = useState(false)
   
    const handleCheckBoxChange = (e) => {
        const {target} = e
        if(target.name === 'received'){
            setShowReceivedMessage(target.checked) 
        }else if(target.name === 'sended'){
            setShowSendedMessage(target.checked);
        }
    }
    

    return ( 
       
        <Box margin={8} padding={5} borderWidth='2px' borderRadius='lg' height='100%' width='400px'>        
             <Heading as='h3' size='lg' marginBottom={2}>{id}</Heading>
                <AccordionCamera id={id}/>
             <LogSendMessage dest={id}/>
             <Stack margin={'0 0 20px 0'} justify='space-between' direction='row'> 
                <div></div>    
                <div>
                    <Checkbox padding={'0 5px'} name='sended'  value={showSendedMessage} onChange={handleCheckBoxChange}>Sent</Checkbox>
                    <Checkbox padding={'0 5px'} defaultChecked name='received' value={showReceivedMessage} onChange={handleCheckBoxChange}> Received </Checkbox>
                </div>
            </Stack>
            
            <LogMessages showSendedMessage={showSendedMessage} showReceivedMessage={showReceivedMessage}  logs={logs}/>
        </Box>
        
        );
    }
    
    export default Card;