import React from 'react';
import {Link} from "react-router-dom";

// use <iframe> to easily embed youtube videos
// right-clicking on the yt video and picking the embed option will provide html code
function TutorialPage() {
  return (
    <div>
      <h1>Tutorials</h1>

      <p>Watch the videos below for a walkthrough of the site's features.</p>

      <h2>1. Import</h2>
      <iframe 
        width="670" 
        height="377" 
        src="https://www.youtube.com/embed/QH00Qkvj6Hw" 
        title="Ranking Tool Tutorial 1 - Importing a File" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        referrerpolicy="strict-origin-when-cross-origin" 
        allowfullscreen
      ></iframe>

      <h2>2. Edit</h2>
      <iframe 
        width="670" 
        height="377" 
        src="https://www.youtube.com/embed/C2iN-Oeleds" 
        title="Ranking Tool Tutorial 2 - Editing a Table" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        referrerpolicy="strict-origin-when-cross-origin" 
        allowfullscreen
      ></iframe>

      <h2>3. Export</h2>
      <iframe 
        width="670" 
        height="377" 
        src="https://www.youtube.com/embed/9WNI9yE1tqA" 
        title="Ranking Tool Tutorial 3 - Exporting to a File" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        referrerpolicy="strict-origin-when-cross-origin" 
        allowfullscreen
      ></iframe>

      

      <div></div>

      <Link to="/">Return</Link>

    </div>
  );
  
}

export default TutorialPage;