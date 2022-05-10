import { createContext, useEffect, useState } from "react";
import * as constants from "./socket_constants";
import { io } from "socket.io-client";

const inDev = true;
const SOCKET_URL = inDev ? "http://127.0.0.1:8000" : null;

const WebSocketContext = createContext(null);

export { WebSocketContext };

export default ({ children }) => {
    const [socket, setSocket] = useState(null);
    const [isOnline, setIsOnline] = useState(false)
    const [logs, setLogs] = useState({});
    const [connectedList, setConnectedList] = useState([]);
    const [socketContext, setSocketContext] = useState({
        socket: null,
        connect: null,
        disconnect: null,
        reconnect: null,
    });
    
    useEffect(() => {
        if(socket){
            socket.emit('send_available_epucks', {list_epucks:connectedList})
        }
    },[connectedList])
    
    const connect = () => {
        
        setSocket(
            io(SOCKET_URL, {
                reconnectionAttempts: 1,
            })
            );
        };
        
        const reconnect = () => {
            socket.connect()
        };
        
        const disconnect = () => {
            socket.disconnect();
        };
        
        useEffect(() => {
            if (socket) {        
                socket.removeAllListeners();
                
                socket.on(constants.CONNECTED, () => {
                    console.log("CONNECTED !");
                    setIsOnline(true)
                    socket.emit('monitor_online', socket.id)
                });
                
                
                socket.on(constants.CONNECT_ERROR, (e) => {
                    console.error("Error Logging");
                    setIsOnline(false)
                });
                
                
                socket.on(constants.DISCONNECTED, () => {
                    console.log("DISCONNECTED !");
                    setSocket(null)
                    setIsOnline(false)
                });
                
                socket.on(constants.NEW_ROBOT, (data) => {
                    const { new_robot, msg } = data;
                    setLogs((prev) => ({ ...prev, [new_robot]: [] }));
                    setConnectedList((prev) => {
                        if(prev.includes(new_robot)){
                            return prev
                        }
                        
                        return [...prev, new_robot]
                    })
                });
                
                socket.on('is_alive', (data) => {
                    
                    const {id} = data
                    
                    setLogs((prev) => {
                        if(!Object.keys(prev).includes(id)){
                            return { ...prev,  [id]: [] }
                        }
                        return prev
                    });
                    
                    setConnectedList((prev) => {
                        if(prev.includes(id)){
                            return prev
                        }
                        
                        return [...prev, id]
                    })
                })
                
                socket.on(constants.SEND_BROADCAST_TO_MONITOR, (data) => {
                    const { from, msg, is_receiver } = data;
                    const timestamp = new Date().getTime();
                    
                    setLogs((prev) => {
                        if(prev[from] === undefined){
                            return {
                                ...prev,
                                [from]: [{clientName: from, timestamp, msg, isReceiver:is_receiver }],
                            }
                        }else{
                            return{
                                ...prev,
                                [from]: [...prev[from], {clientName:from, timestamp, msg, isReceiver:is_receiver }],
                            }
                        }
                    });
                });
                
                socket.on(constants.CONFIRM_RECEPTION, (data) => {
                    const { id, msg, is_receiver, timestamp } = data;
                    
                    setLogs((prev) => {
                        if(prev[id] === undefined){
                            return {
                                ...prev,
                                [id]: [{clientName:id, timestamp, msg, isReceiver:is_receiver }],
                            }
                        }else{
                            return{
                                ...prev,
                                [id]: [...prev[id], {clientName:id, timestamp, msg, isReceiver:is_receiver }],
                            }
                        }
                    });
                    
                });
                
                
                
            } else {
                connect();
            }
            
            return () => {
                if (socket) socket.disconnect();
            };
        }, [socket]);
        
        
        
        
        useEffect(() => {
            setSocketContext({
                socket,
                connect,
                disconnect,
                reconnect,
                isOnline
            });
        }, [SOCKET_URL, socket, isOnline]);
        
        return (
            <WebSocketContext.Provider value={{ socketContext, logs, connectedListState: [connectedList, setConnectedList] }}>
            {children}
            </WebSocketContext.Provider>
            );
        };
        