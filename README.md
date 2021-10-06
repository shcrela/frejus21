# <p style="color: red;">frejus21 - TP Raman Maps - svi workflow
</p>

<!-- #region -->
## Option 1

If you have a Renater account (any university, CNRS, INRAE, etc.)

1. Go to https://jupyterhub.ijclab.in2p3.fr/  
2. Start your server
3. Click on new -> terminal
4. Copy/paste the following command into the terminal: `git clone https://github.com/shcrela/frejus21.git`  
6. Close the terminal after it finishes cloning.
7. Start (Double-click) the first notebook

## Option 2

Run everything locally. (You must have ana(mini)conda installed)

1. Open the terminal[<sup>1</sup>](#fn1) (Anaconda prompt pour Windows) on your computer and navigate to the folder of your choice. 
2. Copy/Paste the following commands into your terminal:
3. `git clone https://github.com/shcrela/frejus21.git` 
4.  `cd frejus21` 

If you don't have git installed, once on the github page clik on the only green button (on top-right of the github page and download zip
 
5. Download the data (click on your group to see the code to copy/paste into your terminal)

<div style="margin-left: 50px">
<details>
  <summary>Example A1</summary>
        wget ./data/exampleA1.wdf "https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013557"
    
    ou bien:
[download link](https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013557)

></details>

<details>
  <summary>Example A2</summary>  
  
        wget ./data/exampleA2.wdf "https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013560" 
    ou bien:
[download link](https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013560)

  
</details>
<details>
  <summary>Example M1</summary>
  

        wget ./data/exampleM1.wdf "https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013556" 
    ou bien:
[download link]("https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013556)

  
</details>
<details>
  <summary>Example M1bis (avoid, too hard)</summary>  
    

        wget ./data/exampleM2.wdf "https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013558"
    ou bien:
[download link]("https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013558)
 
</details>  
<details>
  <summary>Example M3</summary>  
    
 
        wget ./data/exampleM3.wdf "https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013559"
    ou bien:
[download link]("https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013559)
 
</details>  

<details>
  <summary>Example M3bis</summary>  
    

        wget ./data/exampleM4.wdf "https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013563"
    ou bien:
[download link]("https://filesender.renater.fr/download.php?token=91a45abe-86e3-4f9b-bf6c-f6cbfc01b2ec&files_ids=9013563)
 
</details>  
</div>
<div style="color: gray; margin-left: 2em">
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
<!-- #endregion -->

## Option 3 
(you won't be able to do all of the examples)

If neither of the above suits you.

Click on the binder icon

```python

```
