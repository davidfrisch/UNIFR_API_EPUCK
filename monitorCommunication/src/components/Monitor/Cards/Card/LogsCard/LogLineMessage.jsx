import {Flex} from "@chakra-ui/react";
import {memo} from 'react'
const LogLineMessage = ({color, msg, timestamp}) => {   
    return ( 
        <Flex justifyContent='space-between' color={color}>
            <div>{new Date(timestamp).toLocaleTimeString()}</div>
            <div>{msg}</div>
        </Flex>
    );
}
 
export default memo(LogLineMessage);