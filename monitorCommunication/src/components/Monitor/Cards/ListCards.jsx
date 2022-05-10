import { Flex, Wrap, WrapItem } from "@chakra-ui/react"
import { useContext, useEffect } from "react"
import { WebSocketContext } from "../../../context/socket"
import Card from "./Card/Card"


const ListCards = () => {
    
    const contextValues = useContext(WebSocketContext)
    const {logs, connectedListState} = contextValues
    const [connectedList, setConnectedList] = connectedListState
    
    return ( 
        <Wrap>
        {Object.entries(logs).map(([key, val], i) => {
            if(!connectedList.includes(key)){
                return <WrapItem key={key}></WrapItem>
            }

            return (<WrapItem key={key} h='100%'>
                        <Card key={key} id={key} logs={val}/>
                    </WrapItem>)
        })}
            </Wrap> 
            );
        }
        
        export default ListCards;