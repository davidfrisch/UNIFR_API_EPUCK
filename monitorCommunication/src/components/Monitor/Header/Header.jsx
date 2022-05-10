import { RepeatIcon } from "@chakra-ui/icons";
import { Box, Button, Circle, Flex, Heading, useColorMode } from "@chakra-ui/react";
import { useContext } from "react";
import { WebSocketContext } from "../../../context/socket";

const Header = () => {


      const { colorMode, toggleColorMode } = useColorMode()
      const {socketContext} = useContext(WebSocketContext)
      const {isOnline, reconnect} = socketContext
      
    return ( 
        <Flex justifyContent='space-between'>
            <Box>
                {isOnline ?
                    (<Circle size='40px' bg={'green'} color='white'>
                        ON 
                    </Circle>)
                    :
                    (<Button  leftIcon={<RepeatIcon />}  onClick={reconnect}>Reconnect</Button>)
                    }
            </Box>
            <Heading>Monitor Communcation</Heading>
            <Button onClick={toggleColorMode}>Toggle {colorMode === 'light' ? 'Dark' : 'Light'}</Button>
        </Flex>
     );
}
 
export default Header;