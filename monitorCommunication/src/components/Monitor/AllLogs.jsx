import { Box, Flex, useColorMode, useColorModeValue } from "@chakra-ui/react";
import { useContext, useEffect, useState } from "react";
import { WebSocketContext } from "../../context/socket";

const sortLogs = (log1, log2) => {
    return log1.timestamp - log2.timestamp;
}

const AllLogs = () => {
    const { colorMode } = useColorMode()
    const color = useColorModeValue('dark', 'white')

    const contextValues = useContext(WebSocketContext)

    const {logs} = contextValues
    const [allLogs, setAllLogs] = useState(()=>{return Object.values(logs).flat().sort(sortLogs)})

    useEffect(()=>{
        setAllLogs(()=>{return  Object.values(logs).flat().sort(sortLogs)})
    },[logs])

    return ( 
    <Box height='80vh' overflowY='scroll'>
        {allLogs.map(({clientName, isReceiver, msg, timestamp}, index) => (<div key={index}>
            <Flex width='50%' padding={'0 12px'} justify='space-between' color={isReceiver ? colorMode === 'light' ? '#0000ff' : '#82AAFF' : color}>
                  <div> @{new Date(timestamp).toLocaleTimeString()} - {clientName} {isReceiver ? 'received': 'sent'}:</div>
                  <div>{msg}</div>
            </Flex>
        </div>))}
    </Box> );
}
 
export default AllLogs;