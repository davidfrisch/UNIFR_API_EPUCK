import {useEffect, useContext, useState} from 'react'
import { WebSocketContext } from '../../../../../context/socket'
import { Image, Heading, Box } from '@chakra-ui/react'
import imageNotFound from '../../../../../../images/noCamera.jpg'

const SingleLiveStream = ({img}) => {

    return ( 
        <Box>
            <Image height='120px' width='160px' src={img ? img : imageNotFound}/>
        </Box> );
    }
    
    export default SingleLiveStream;