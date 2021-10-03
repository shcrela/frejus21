# <p style="color: red;">frejus21
</p>


## Option 1

Run everything locally. (You must have miniconda/anaconda installed)

1. Open the terminal[<sup>1</sup>](#fn1) on your computer and navigate to the folder of your choice. 
2. Copy/Paste the following commands into your terminal:
3. `git clone https://github.com/shcrela/frejus21.git`  
4.  `cd frejus21`  
5. Download the data (click on your group to see the code to copy/paste into your terminal)

<div style="margin-left: 50px">
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
</div>
<div style="color: gray; margin-left: 1em">
<details>
    <summary>6. Optionally (create new conda environment)</summary>
    <pre>conda env create -f environment.yml</pre>
    <pre>conda activate frejus21</pre>  
</details>
</div>  

7. Start the jupyter lab/notebook
8. Open the first notebook  

<span id="fn1"><sup>1</sup></span> <span style="font-size: smaller">If you're on Windows, then the _Terminal_ would be the [Anaconda prompt](https://www.youtube.com/watch?v=UAUO_K-bRMs).</br>(click on the windows sign on your keyboard and type `anaconda prompt`
</span>
## Option 2

If you have a Renater account (any university, CNRS, INRAE, etc.)

1. Go to https://jupyterhub.ijclab.in2p3.fr/  
2. Start your server
3. Click on new -> terminal
4. Copy/paste the following command into the terminal: `git clone https://github.com/shcrela/frejus21.git`  
6. Close the terminal after it finishes cloning.
7. Start (Double-click) the first notebook

## Option 3 
(you won't be able to do all of the examples)

If neither of the above suits you.

Click on the binder icon
