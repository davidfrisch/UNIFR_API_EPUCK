import {useEffect, useContext, useState} from 'react'
import { WebSocketContext } from '../../../../../../context/socket'
import { Image, Heading, Box } from '@chakra-ui/react'

const SingleLiveStream = () => {
    const contextValues = useContext(WebSocketContext)
    const {socket} = contextValues.socketContext
    const [img, setImg] = useState(null)

    useEffect(()=>{
        if(socket){
            socket.on('stream_img_monitor', (data) => {
                const image = data
                const arrayBufferView = new Uint8Array(image);
                const blob = new Blob( [ arrayBufferView ], { type: "image/jpeg" } );
                const img_url = URL.createObjectURL(blob);
                setImg(img_url)
            })
        }
    },[socket])
    return ( 
        <Box>
            {img && <Image height='120px' width='160px' src={img}/>}
        </Box> );
    }
    
    export default SingleLiveStream;