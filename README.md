# frejus21


## Option 1

Create a conda environment on your computer and run everything locally.

1. Open the terminal on your computer and navigate to the folder of your choice. 
2. Copy/Paste the following commands into your terminal:
3. `git clone https://github.com/shcrela/frejus21.git`  
4.  `cd frejus21`
5. `conda env create -f environment.yml`
6. Downloading data (click on your group to see the code to copy/paste into your terminal)
<details>
  <summary>Group A1</summary>
  
  ```bash
    wget ./data/exampleA1.wdf "https://filesender.renater.fr/download.php?token=970bff29-0d7e-4106-a128-0d6c34488c4f&files_ids=8905055"
  ```
</details>
<details>
  <summary>Group A2</summary>
  
  ```bash
    wget ./data/exampleA2.wdf "https://filesender.renater.fr/download.php?token=970bff29-0d7e-4106-a128-0d6c34488c4f&files_ids=8905055"
  ```
</details>
<details>
  <summary>Group B1</summary>
  
  ```bash
    wget ./data/exampleB1.wdf "https://filesender.renater.fr/download.php?token=970bff29-0d7e-4106-a128-0d6c34488c4f&files_ids=8905055"
  ```
</details>
<details>
  <summary>Group B2</summary>  
  ```bash
    wget ./data/exampleB2.wdf "https://filesender.renater.fr/download.php?token=970bff29-0d7e-4106-a128-0d6c34488c4f&files_ids=8905055"
  ```
</details>  

7. start the jupyter lab/notebook
8. Open the first notebook

## Option 2

You don't want to install anything *AND* you have a Renater account (any university, CNRS, INRAE, etc.)

1. Go to https://jupyterhub.ijclab.in2p3.fr/  
2. Start your server
3. Click on new -> terminal
4. Copy/paste the following command: `git clone https://github.com/shcrela/frejus21.git`  
6. Close the terminal after it finishes cloning.
7. Double-click on the first notebook

## Option 3

If neither of the above suits you.

Click on the binder icon
