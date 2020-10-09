import javax.swing.*;        
import java.util.Arrays;

public class RouterNode {
  private int myID;
  private GuiTextArea myGUI;
  private RouterSimulator sim;
  private int[] costs = new int[RouterSimulator.NUM_NODES];
  private int[][] distanceTable = new int[RouterSimulator.NUM_NODES][RouterSimulator.NUM_NODES];
  private int[] routesList = new int[RouterSimulator.NUM_NODES];
  
  // Program parameters
  private int CONST_TAB_SIZE = 12; // Constant used to set column width
  private boolean POISONED_REVERSE = false;
  
  /*	TDTS06 - Mayeul G. & Pierre M. - Lab 4
   * 	
   * 	TODO:
   * 		- Implement a Update function for when we receive  
   * 		  a packet or when a link cost change
   * 		- Implement poisoned reverse in the sendUpdate() 
   * 		  function
   *  
   */
  

  //--------------------------------------------------
  // Virtual router constructor, init. base values, distance table, routes table & costs table
  public RouterNode(int ID, RouterSimulator sim, int[] costs) {
    myID = ID;
    this.sim = sim;
    myGUI = new GuiTextArea("  Output window for Router #"+ ID + "  ");

    System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);
    
    
    // Route list initialisation
    for (int i = 0; i < sim.NUM_NODES; i++) {
        if (costs[i] != sim.INFINITY){routesList[i] = i;} 
        else{routesList[i] = -1;}
    }
    
    // Distance table initialisation
    for (int[] row: distanceTable) {Arrays.fill(row, sim.INFINITY);}
    distanceTable[myID] = Arrays.copyOf(costs, costs.length);
    
    printDistanceTable();
  }

  
  //--------------------------------------------------
  // Update the route list from the distanceTable
  private boolean Update() {
	  boolean updt = false;
	  for (int i = 0; i < sim.NUM_NODES; i++) {
		  // We ignore ourself
		  if (i == myID) {continue;}

		  int newRouteCost = sim.INFINITY;
		  
		  // We keep the old values in memory
		  int oldRoute = routesList[i];
		  int oldRouteCost = distanceTable[myID][i];

		  for (int j = 0; j < sim.NUM_NODES; j++){
			  // We keep ignoring ourself
			  if (j == myID) {continue;}
			  
			  // If this is a neighbour AND if the new searched route is greater than the actual distance AND if it is not us
			  if(costs[j] != RouterSimulator.INFINITY && newRouteCost > distanceTable[j][i] + costs[j] && j != myID){
				  distanceTable[myID][i] = distanceTable[j][i] + costs[j];
                  newRouteCost = distanceTable[myID][i];
				  routesList[i] = j;
			  }
		  }
		  if(oldRoute != routesList[i] || oldRouteCost != distanceTable[myID][i]){
			  updt = true;
		  }
	  }
	  return updt;
  }
  
  
  //--------------------------------------------------
  public void recvUpdate(RouterPacket pkt) {
	  DEBUG("Rcv packet !");
	  // Updating the distance table
	  distanceTable[pkt.sourceid] = pkt.mincost;
	  // Updating the routes list from the distance table
	  // and send this update to all neighbour if there
	  // are changes
	  if (Update()) {sendUpdate();}
  }
  

  //--------------------------------------------------
  private void sendUpdate() {
	  for (int i = 0; i < sim.NUM_NODES; i++) {
		  int[] sendedCosts = Arrays.copyOf(distanceTable[myID],sim.NUM_NODES);
		  
		  // We ignore non-neighbor nodes
	      if(i == myID || costs[i] == sim.INFINITY) {continue;}
	      
	      if(POISONED_REVERSE) {
	    	  for (int j = 0; j < RouterSimulator.NUM_NODES; j++) {
	    		  if (routesList[j] == i && j != i) {
	    			  sendedCosts[j] = RouterSimulator.INFINITY;
	    		  }
	    	  }
	      }
	      RouterPacket pkt = new RouterPacket(myID,i,sendedCosts);
	      DEBUG("Sending updt !");
	      sim.toLayer2(pkt);
	  }
 }
  
  private void printTabHeader() {
	  myGUI.print(F.format("dst",CONST_TAB_SIZE) + " |");
	  for (int i = 0; i < sim.NUM_NODES ; i++) {myGUI.print(F.format(i,CONST_TAB_SIZE));}
	  myGUI.println("");
	  for (int i = 0; i < sim.NUM_NODES ; i++) {
		  for (int j = 0; j <= 1.5*CONST_TAB_SIZE; j++) {
			  myGUI.print("-");
		  }
	  }
	  myGUI.println("");
  }

  //--------------------------------------------------
  public void printDistanceTable() {
	  // Header
	  myGUI.println("Current table for " + myID +
			"  at time " + sim.getClocktime());
	  myGUI.println("");
	  
	  // DistanceTable
	  myGUI.println("Distancetable: ");
	  printTabHeader();
	  
	  // Printing a line for each known routers
	  for (int i = 0; i < sim.NUM_NODES; ++i ) {
		  // We ignore non-neighbor nodes
	      if (costs[i] == sim.INFINITY) continue;
	      
	      myGUI.print(F.format("nbr  " + i, CONST_TAB_SIZE) + "|");
	      for (int j = 0; j < sim.NUM_NODES; ++j ) {myGUI.print(F.format(distanceTable[i][j],CONST_TAB_SIZE));}
	      myGUI.println("");
	    }
	  myGUI.println("");
	  
	  // Distance vector & routes
	  myGUI.println("Our distance vector and routes: ");
	  printTabHeader();
	  
	  // Printing costs
	  myGUI.print(F.format("cost",CONST_TAB_SIZE) + "|");
	  for (int i = 0; i < sim.NUM_NODES; i++) {
	      myGUI.print(F.format(costs[i],CONST_TAB_SIZE));
	  }
	  myGUI.println("");
	  // Printing routes
	  myGUI.print(F.format("route",CONST_TAB_SIZE) + "|");
	  for (int i = 0; i < sim.NUM_NODES; i++) {
	      myGUI.print(F.format(routesList[i],CONST_TAB_SIZE));
	  }
	  myGUI.println("");
  }

  //--------------------------------------------------
  public void updateLinkCost(int dest, int newcost) {
	  costs[dest] = newcost;
	  if (Update()) {sendUpdate();}
  }
  
  // DEBUG FUNCTION - TO REMOVE
  private void DEBUG(String str) {
	  myGUI.print(" DEBUG from " + myID + "  at time " + sim.getClocktime() + ": ");
	  myGUI.println(str);
  }
}


