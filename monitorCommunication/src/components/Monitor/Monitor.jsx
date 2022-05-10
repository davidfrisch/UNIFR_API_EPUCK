import { Box, Flex, Heading } from "@chakra-ui/react";
import { useContext, useEffect, useState } from "react";
import { WebSocketContext } from "../../context/socket";
import ButtonWhoIsAlive from "./ButtonWhoIsAlive";
import Header from "./Header/Header";
import InputBroadcast from "./InputBroadcast/InputBroadcast";
import TabsMonitor from "./TabsMonitor";


const Monitor = () => {
    const {socketContext} = useContext(WebSocketContext)    
    const {isOnline} = socketContext
    
    return ( 
        <Box padding='20px 20px 0 20px'>
        <Header/>
        { isOnline ?  
            ( <Box margin={'20px 0'}>
                <Flex alignItems='end' justifyContent='center' width='100%'>
                <ButtonWhoIsAlive/>
                <InputBroadcast/>
                </Flex>
                <TabsMonitor/>
                </Box>
            )
                :
                
            (<Heading color="red">No connection to socket host</Heading>)
            }
        </Box> 
            );
        }
        
        export default Monitor;