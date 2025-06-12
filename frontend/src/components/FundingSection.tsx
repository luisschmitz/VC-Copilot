"use client";

import { FundingNewsResponse, FundingRound, NewsItem } from '@/types/api';

interface FundingSectionProps {
  fundingData: FundingNewsResponse;
}

export default function FundingSection({ fundingData }: FundingSectionProps) {
  const {
    company_name,
    total_funding,
    funding_rounds,
    latest_news,
    funding_status,
    notable_investors,
    last_funding_date
  } = fundingData;

  return (
    <div>
      <h2 className="text-lg font-medium text-gray-900 mb-4">💰 Funding History & News</h2>
      
      {/* Funding Summary */}
      <div className="bg-indigo-50 rounded-md p-4 mb-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
          {total_funding && (
            <div>
              <h3 className="text-sm font-medium text-indigo-800">Total Funding</h3>
              <p className="text-lg font-semibold text-indigo-900">{total_funding}</p>
            </div>
          )}
          {last_funding_date && (
            <div>
              <h3 className="text-sm font-medium text-indigo-800">Last Funding</h3>
              <p className="text-lg font-semibold text-indigo-900">{last_funding_date}</p>
            </div>
          )}
          {funding_status && (
            <div>
              <h3 className="text-sm font-medium text-indigo-800">Status</h3>
              <p className="text-lg font-semibold text-indigo-900">{funding_status}</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Funding Rounds */}
      <div className="mb-8">
        <h3 className="text-md font-medium text-gray-700 mb-3">Funding Rounds</h3>
        {funding_rounds && funding_rounds.length > 0 ? (
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Date</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Round</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Amount</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Lead Investors</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {funding_rounds.map((round, index) => (
                  <tr key={index}>
                    <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900 sm:pl-6">{round.date || 'Unknown'}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">{round.round_type || 'Unknown'}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">{round.amount || 'Undisclosed'}</td>
                    <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                      {round.lead_investors && round.lead_investors.length > 0 
                        ? round.lead_investors.join(', ') 
                        : 'Undisclosed'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 italic">No funding rounds data available.</p>
        )}
      </div>
      
      {/* Notable Investors */}
      {notable_investors && notable_investors.length > 0 && (
        <div className="mb-8">
          <h3 className="text-md font-medium text-gray-700 mb-2">Notable Investors</h3>
          <div className="flex flex-wrap gap-2">
            {notable_investors.map((investor, index) => (
              <span key={index} className="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-green-100 text-green-800">
                {investor}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Latest News */}
      <div>
        <h3 className="text-md font-medium text-gray-700 mb-3">Latest News</h3>
        {latest_news && latest_news.length > 0 ? (
          <div className="flow-root">
            <ul role="list" className="-my-5 divide-y divide-gray-200">
              {latest_news.map((item, index) => (
                <li key={index} className="py-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{item.title}</p>
                      <p className="text-sm text-gray-500 line-clamp-2">{item.summary}</p>
                      <div className="flex items-center mt-1">
                        {item.date && (
                          <span className="text-xs text-gray-500">{item.date}</span>
                        )}
                        {item.source && (
                          <>
                            <span className="mx-1 text-gray-500">•</span>
                            <span className="text-xs text-gray-500">{item.source}</span>
                          </>
                        )}
                      </div>
                    </div>
                    {item.url && (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center shadow-sm px-2.5 py-0.5 border border-gray-300 text-sm leading-5 font-medium rounded-full text-gray-700 bg-white hover:bg-gray-50"
                      >
                        View
                      </a>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="text-gray-500 italic">No news data available.</p>
        )}
      </div>
    </div>
  );
}
