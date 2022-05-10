import { ViewOffIcon } from '@chakra-ui/icons';
import {
    Accordion,
    AccordionItem,
    AccordionButton,
    AccordionPanel,
    AccordionIcon,
    Box,
    Flex
} from '@chakra-ui/react'
import { useContext, useEffect, useRef, useState } from 'react';
import { WebSocketContext } from '../../../../../context/socket';
import SingleLiveStream from './SingleLiveStream';

const AccordionCamera = ({id}) => {
    const contextValues = useContext(WebSocketContext)
    const {socket} = contextValues.socketContext
    const [img, setImg] = useState(null)
    const [hasStart, setHasStart] = useState(false)
    const refHasStart = useRef(false)

    useEffect(()=>{
        refHasStart.current = hasStart
    },[hasStart])

    useEffect(()=>{
        if(socket){
            socket.on(`${id}_init_camera`, (data) => {
                console.log(id+ 'start camera')
                setHasStart(true)
            })
            
            socket.on(`${id}_stream_img_monitor`, (data) => {
                if(refHasStart.current){
                    const image = data
                    const arrayBufferView = new Uint8Array(image);
                    const blob = new Blob( [ arrayBufferView ], { type: "image/jpeg" } );
                    const img_url = URL.createObjectURL(blob);
                    setImg(img_url)
                } 
            })
            
            socket.on(`${id}_disable_camera`, (data) => {
                setImg(null)
                setHasStart(false)
            })
        }
    },[socket])
    
    return ( 
        <Accordion allowMultiple>
        <AccordionItem>
        <h2>
        <AccordionButton>
        <Box flex='1' textAlign='left'>
        {hasStart && img ? 'Online' : <ViewOffIcon/>} Live Camera
        </Box>
        <AccordionIcon />
        </AccordionButton>
        </h2>
        <AccordionPanel pb={4} justifyContent="center">
        <Flex justifyContent='center'>
        <SingleLiveStream img={img}/>
        </Flex>
        </AccordionPanel>
        </AccordionItem>
        </Accordion>
        );
    }
    
    export default AccordionCamera;