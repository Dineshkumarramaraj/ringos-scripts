import re
import subprocess
import logging
import os
import sys

#Default values
objPath="/root/ring-building/"
port="6000"
weight="25"
region="1"
zone="1"

def nodeSplit(nodes):
   nodeslist= []
   rows= re.split("\+-*\+\n?",nodes)[2:-1]
   nrow=re.split('\n',rows[0])[:-1]
   for r in nrow:
      nodelist=re.split("\|",r)
      nodeslist.append(nodelist[1].strip())
   return nodeslist

def checkDisks(nodes):
   nodeslist= []
   diskslist=[]
   cmd = "ringos list-disks -n %s" %nodes
   p=subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
   (output,err) = p.communicate()
   rows= re.split("\+-*\+-*\+\n?",output)[2:-1]
   nrow=re.split('\n',rows[0])[:-1:2]
   for r in nrow:
      nodelist=re.split("\|",r)
      nodeslist.append(nodelist[1].strip())
      diskslist.append(nodelist[2].strip())

   logger.info(nodeslist)
   logger.info(diskslist)
   if nodeslist.__len__() > 1:
      return True
   else:
      return False

def disksFormat(nodes,ring):
    disks,labels,formatted = [],[],[]
    cmd =  "ringos format-disks -n %s -d all -f" %nodes
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
    (output,err)=p.communicate()
    logger.info(output)
    pairs = re.split("\+-*\+-*\+-*\+-*\+-*\+-*\+\n?",output)[2:-1]

    lines = re.split("\n?",pairs[0])[:-1:2]
    for p in lines:
       col=re.split("\|",p)
       disks.append(col[1].strip())
       labels.append(col[5].strip())
       formatted.append(col[2].strip())

    logger.info(disks)
    logger.info(labels)
    logger.info(formatted)

    if disks.__len__() >= 1:
        for i in range(disks.__len__()):
          path=objPath+ring
          acmd="ringos add-disk-to-ring -f %s -i %s -p %s -d %s -w %s -r %s -z %s" %(path,nodes,port,labels[i],weight,region,zone)
          if formatted[i] == "y":
             c=subprocess.Popen(acmd,stdout=subprocess.PIPE,shell=True)
             (op,error)=c.communicate()
             logger.info(op)
          else:
             print("Disk is not formatted")
             pass
       return True
    else:
       return False


if __name__=='__main__':
   starter = False
   object = False
   ring="object.builder"
   print "\t\t\t\"Welcome to add Disks script\"\n"
   handler=logging.FileHandler('/var/log/adddisks.log')
   logger=logging.getLogger('adddisks')
   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   date_format='%b %d %Y %H:%M:%S'
   formatter=logging.Formatter(fmt=format, datefmt=date_format)
   handler.setFormatter(formatter)
   logger.addHandler(handler)
   logger.setLevel(logging.INFO)

   objFileExist = os.path.isfile("/root/ring-building/object.builder")
   if objFileExist != True:
      logger.info("Object.builder file is not available.")
      print "Error: Object.builder file is not available in /root/ring-building directory."
      sys.exit(0)

   logger.info("object.builder is available.")
   ''' Get the input from the user to add the disks for either Starter or object nodes'''
   ask=raw_input("Which node do you want to add disks. Please select the following options \n 1. Starter \n 2. Scale out Object \n 3. Exit\n")
   while True:
      if ask in ['1']:
         p=subprocess.Popen("ringos list-swift-nodes -t starter",stdout=subprocess.PIPE,shell=True)
         (output,err) = p.communicate()
         if err == None:
            sNodes=nodeSplit(output)
            if sNodes != None:
               print "Number of Starter Nodes available in Cloud:",sNodes.__len__(),"\t",sNodes
               starter = True
               break

      elif ask in ['2']:
         input=raw_input("For Scale Out Object, do you want to use \n 1. Existing object builder(Ring 0) \n 2. Create a new object-1 builder(Ring 1) \n")
         if input in ['1']:
            ring="object.builder"
         elif input in ['2']:
            ring="object-1.builder"
            obj1FileExist=os.path.isfile("/root/ring-building/object-1.builder")
            if obj1FileExist != True:
               logger.info("Object-1 builder file is not available.")
               print "Error: Object-1.builder file is not available in /root/ring-building directory."
               sys.exit(0)
         else:
           print "Wrong Choice, Exiting.........."
           sys.exit(0)
         p=subprocess.Popen("ringos list-swift-nodes -t object",stdout=subprocess.PIPE,shell=True)
         (output,err) = p.communicate()
         if err == None:
            oNodes=nodeSplit(output)
            if oNodes != None:
               print "Number of Scale Out Object Nodes are available in Cloud:",oNodes.__len__(),"\t",oNodes
               object = True
               break

      elif ask in ['3']:
         sys.exit(0)

      else:
         ask=raw_input("Which node do you want to add disks. Please select the following options \n 1. Starter \n 2. Scale out Object \n 3. Exit\n")

   if starter == True:
      for i in sNodes:
        availDisks=checkDisks(i)
        if availDisks == True:
           logger.info("Disks are available")
           format=disksFormat(i,ring)
           if format == True:
              logger.info("Disk formatted")
           else:
              logger.info("Some problem in formatting the disks")
        else:
           print "Disks are not available for", i, "Please check it"
           break

   if object == True:
      for i in oNodes:
        aveilDisks=checkDisks(i)
        if aveilDisks ==True:
           logger.info("Disks are available")
           fmt=disksFormat(i,ring)
           if fmt == True:
              logger.info("Disk formateed")
           else:
              logger.info("some problem in formatting the disks")
        else:
           print "Disks are not available for",i,"Please check it"
           break

   print "Disks are added to Ring. Please rebalance the ring and copy the same into respective nodes"


