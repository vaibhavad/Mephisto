import React from "react";
import { useTable } from "react-table";
import { createAsync } from "../lib/Async";
import useAxios from "axios-hooks";
import { ButtonGroup } from "@blueprintjs/core";
import { Link } from "react-router-dom";
import { reviewActions } from "../service";

const GridReviewAsync = createAsync();

function GridReviewWithData({ id }) {
  const gridReviewAsync = useAxios({
    url: "data/submitted_data?task_run_id=" + id
  });

  return (
    <GridReviewAsync
      info={gridReviewAsync}
      onData={({ data }) => (
        <div>
          <GridReview data={data} id={id} />
        </div>
      )}
      onError={() => null}
      onLoading={() => null}
      onEmptyData={() => <div>There are no units to review...</div>}
      checkIfEmptyFn={data => data.units}
    />
  );
}

function GridReview({ data, id }) {
  const sampleTestData = [
    {
      assignment_id: "179",
      data: {
        inputs: {
          character_description: "I'm a character loaded from Mephisto!",
          character_name: "Loaded Character 1",
          html: "demo_task.html"
        },
        outputs: { rating: "good" }
      },
      status: "expired",
      task_run_id: "136",
      unit_id: "231",
      worker_id: "10"
    }
  ];

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow
  } = useTable({
    // data: sampleTestData,
    data: data.units,
    columns: [
      { Header: "Assignment ID", accessor: "assignment_id" },
      { Header: "Unit ID", accessor: "unit_id" },
      { Header: "Worker ID", accessor: "worker_id" },
      {
        Header: "Input",
        accessor: "data.inputs",
        Cell: ({ cell: { value } }) => JSON.stringify(value, null, 1)
      },
      {
        Header: "Output",
        accessor: "data.outputs",
        Cell: ({ cell: { value } }) => JSON.stringify(value, null, 1)
      },
      {
        Header: "Status",
        accessor: "status",
        Cell: ({ cell: { value } }) => (
          <span className="bp3-tag bp3-minimal">{value}</span>
        )
      },
      {
        Header: "Actions",
        Cell: ({ cell: { row } }) => {
          const unitId = row.values.unit_id;
          return (
            <div>
              <ButtonGroup>
                <button
                  className="bp3-button bp3-small"
                  onClick={() => reviewActions.accept(unitId)}
                >
                  Accept &amp; Pay
                </button>
                <button
                  className="bp3-button bp3-small"
                  onClick={() => reviewActions.rejectAndPay(unitId)}
                >
                  Reject &amp; Pay
                </button>
                <button
                  className="bp3-button bp3-small"
                  onClick={() => reviewActions.softBlock(unitId)}
                >
                  Soft Block
                </button>
                <button
                  className="bp3-button bp3-small"
                  onClick={() => reviewActions.hardBlock(unitId)}
                >
                  Hard Block
                </button>
              </ButtonGroup>
            </div>
          );
        }
      }
    ]
  });
  return (
    <div>
      <div style={{ margin: "10px 0px" }}>
        <Link to="/">&laquo; Return</Link>
      </div>
      <h3>Task Run #{id}</h3>
      <table
        className="bp3-html-table-striped bp3-html-table"
        {...getTableProps()}
      >
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()}>{column.render("Header")}</th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row, i) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => {
                  return (
                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default GridReviewWithData;
