import javax.swing.*;        

public class RouterNode {
  private int myID;
  private GuiTextArea myGUI;
  private RouterSimulator sim;
  private int[] costs = new int[RouterSimulator.NUM_NODES];
  private int[][] distanceTable = new int[RouterSimulator.NUM_NODES][RouterSimulator.NUM_NODES];
  private int CONST_TAB_SIZE = 10;

  //--------------------------------------------------
  public RouterNode(int ID, RouterSimulator sim, int[] costs) {
    myID = ID;
    this.sim = sim;
    myGUI =new GuiTextArea("  Output window for Router #"+ ID + "  ");

    System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);
    printDistanceTable();
  }

  //--------------------------------------------------
  public void recvUpdate(RouterPacket pkt) {

  }
  

  //--------------------------------------------------
  private void sendUpdate(RouterPacket pkt) {
    sim.toLayer2(pkt);

  }
  
  private void printTabHeader() {
	  myGUI.print(F.format("dst",CONST_TAB_SIZE) + " |");
	  for (int i = 0; i < sim.NUM_NODES ; i++) {myGUI.print(F.format(i,CONST_TAB_SIZE));}
	  myGUI.println("");
	  myGUI.println("----------------------------------TEST--------------------------------");
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
	  for (int i = 0 ; i < sim.NUM_NODES ; ++i ) {
	      if (costs[i] == sim.INFINITY) continue;
	      
	      myGUI.print(F.format("nbr  " + i, CONST_TAB_SIZE) + "|");
	      for (int j = 0; j < sim.NUM_NODES; ++j ) {myGUI.print(F.format(distanceTable[i][j],CONST_TAB_SIZE));}
	      myGUI.println("");
	    }
	  myGUI.println("");
	  
	  // Distance vector & routes
	  myGUI.println("Our distance vector and routes: ");
	  printTabHeader();
	  
	  myGUI.println("TO BE IMPLEMENTED...");
	  
  }

  //--------------------------------------------------
  public void updateLinkCost(int dest, int newcost) {
  }

}
