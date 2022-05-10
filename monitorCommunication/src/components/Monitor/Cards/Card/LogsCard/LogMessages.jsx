import { Box, Checkbox, Flex, Stack, useColorMode, useColorModeValue } from "@chakra-ui/react";
import { useState } from "react";
import LogLineMessage from "./LogLineMessage";

const LogMessages = ({showSendedMessage, showReceivedMessage, logs}) => {
    
    const { colorMode } = useColorMode()
    const color = useColorModeValue('dark', 'white')

    
    return ( 
        <Box height='200px' overflowY='scroll' padding={'0 12px'} >
        {logs.length > 0 && logs.map(({timestamp, msg, isReceiver}, index)=>{
            if(isReceiver && showReceivedMessage){
                return ( 
                        <LogLineMessage key={index} timestamp={timestamp} msg={msg} color={isReceiver ? colorMode === 'light' ? '#0000ff' : '#82AAFF' : color} />
                    )
            }else if(!isReceiver && showSendedMessage){
                return (
                    <LogLineMessage key={index} timestamp={timestamp} msg={msg} color={isReceiver ? '#0000ff' : color} />
                )
            }   
                return null
        })}
                </Box> 
               );
            }
            
            export default LogMessages;