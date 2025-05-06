import {Link} from "react-router-dom";

function FAQPage() {
  return (
    <div className="faq-page">
      <h1>Frequently Asked Questions</h1>

      <dl>
        <dt>How do I upload data?</dt>
        <dd>
          You can upload a file in either CSV or TSV format. Or, you can manually add data using the integrated spreadsheet-like data editing tool.
        </dd>

        <dt>How should I format uploaded data?</dt>
        <dd>
          Entries should be entered in the form ‘X - X’, separated by a delimiter (a comma or tab, depending on the filetype). 
          This includes unplayed matchups, which should be represented by ‘0 - 0’. The program will automatically recognize how many players/teams are in your league.
        </dd>

        <dt>Can I edit data after uploading it?</dt>
        <dd>
          Yes! Even after uploading data from a file, you can update entries.
        </dd>

        <dt>Why do I need to create an account?</dt>
        <dd>
          Account making is a simple process that needs only a username and password. Creating an account allows users to save their data to be used for later visits.
        </dd>

        <dt>Can I share league data with others?</dt>
        <dd>
          Yes, rankings and data visualizations can be exported via shareable link.
        </dd>
      </dl>

      <Link to="/">Return</Link>
    </div>
  );
}

export default FAQPage;