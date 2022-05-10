import { Tab, TabList, TabPanel, TabPanels, Tabs } from "@chakra-ui/react";
import AllLogs from "./AllLogs";
import ListCards from "./Cards/ListCards";

const TabsMonitor = () => {
    return ( 
        <Tabs>
            <TabList>
                <Tab>Cards</Tab>
                <Tab>All Logs</Tab>
            </TabList>

            <TabPanels>
                <TabPanel>
                    <ListCards />
                </TabPanel>
                <TabPanel>
                    <AllLogs/>
                </TabPanel>
            </TabPanels>
        </Tabs>
     );
}
 
export default TabsMonitor;