import {Link} from "react-router-dom";

function HomePage() {
  return (
    <div className="home-page">
      <h1>Home Page</h1>

      <dl>
        Hello, welcome to my easy-to-use 1v1 ranking tool. This tool is used to algorithmically sort a list of participants based on their head-to-head data,
         creating an easy method for sports analysts, competitive leagues, and fantasy betters alike to produce accurate rankings of their players. Start by 
         importing a CSV file of your data. Feel free to browse the FAQ and tutorials pages for helpful tips.
      </dl>

      <Link to="/import">Import a CSV file</Link>
    </div>
  );
}

export default HomePage;