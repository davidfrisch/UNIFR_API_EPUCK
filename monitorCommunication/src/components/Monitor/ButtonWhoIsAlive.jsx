import { Button, Box } from "@chakra-ui/react";
import { useContext } from "react";
import { WebSocketContext } from "../../context/socket";

const ButtonWhoIsAlive = () => {

    const contextValues = useContext(WebSocketContext)
    const {connectedListState} = contextValues
    const {socket} = contextValues.socketContext
    const [connectedList, setConnectedList] = connectedListState

    const handleWhoIsAlive = () => {
        setConnectedList([])
        socket.emit('ask_who_is_alive')
    }

    return ( 
        <Box>
            <Button onClick={handleWhoIsAlive}>Who is alive ? </Button>
        </Box> );
}
 
export default ButtonWhoIsAlive;