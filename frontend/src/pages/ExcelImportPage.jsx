import React, { useState, useRef } from 'react';
import { 
  FileSpreadsheet, 
  UploadCloud, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  RefreshCw, 
  ArrowRight,
  ShieldCheck,
  FileCheck 
} from 'lucide-react';
import api from '../api/client';

const ExcelImportPage = ({ onNavigate }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [error, setError] = useState('');
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setError('');
      setPreviewData(null);
      setImportResult(null);
    }
  };

  const handleValidatePreview = async () => {
    if (!file) {
      setError('Please select an Excel or CSV file.');
      return;
    }

    setUploading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/excel/preview/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setPreviewData(res.data);
    } catch (err) {
      setError(err.message || 'Failed to parse and validate file.');
    } finally {
      setUploading(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!previewData?.valid_rows?.length) return;

    setImporting(true);
    setError('');

    try {
      const res = await api.post('/excel/confirm/', {
        accounts: previewData.valid_rows,
      });
      setImportResult(res.data);
    } catch (err) {
      setError(err.message || 'Failed to import customer records.');
    } finally {
      setImporting(false);
    }
  };

  const resetAll = () => {
    setFile(null);
    setPreviewData(null);
    setImportResult(null);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Customer Excel Batch Import
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Two-stage batch intake: Parse & validate customer records with row-level error reporting before confirming import.
          </p>
        </div>

        <a
          href="/api/excel/template/"
          download="visa_customers_template.xlsx"
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors shrink-0"
        >
          <Download className="w-4 h-4 text-blue-400" />
          Download Sample Template (.xlsx)
        </a>
      </div>

      {/* Success State Screen */}
      {importResult ? (
        <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-2xl p-8 text-center space-y-4 animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center mx-auto text-emerald-400">
            <FileCheck className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-white">Import Completed Successfully!</h3>
          <p className="text-sm text-slate-300 max-w-md mx-auto">
            {importResult.message || `Successfully created ${importResult.imported_count} customer records in Pending status.`}
          </p>

          <div className="flex items-center justify-center gap-3 pt-4">
            <button
              onClick={resetAll}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 transition-colors"
            >
              Import Another File
            </button>
            <button
              onClick={() => onNavigate('customers')}
              className="flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20 transition-all"
            >
              View Customers Table <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Upload Area */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <div
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                file
                  ? 'border-blue-500/60 bg-blue-500/5'
                  : 'border-slate-700 hover:border-slate-500 bg-slate-950/40'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileChange}
                className="hidden"
              />
              <div className="w-12 h-12 rounded-xl bg-blue-600/10 border border-blue-500/20 flex items-center justify-center mx-auto mb-3 text-blue-400">
                <UploadCloud className="w-6 h-6" />
              </div>

              {file ? (
                <div>
                  <div className="text-sm font-semibold text-white">{file.name}</div>
                  <div className="text-xs text-slate-400 mt-1">
                    {(file.size / 1024).toFixed(1)} KB • Click to change file
                  </div>
                </div>
              ) : (
                <div>
                  <div className="text-sm font-semibold text-slate-200">
                    Click to select an Excel or CSV file
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Supports .xlsx, .xls, .csv (Max 10MB)
                  </div>
                </div>
              )}
            </div>

            {error && (
              <div className="mt-4 p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            <div className="mt-4 flex items-center justify-between pt-2">
              <div className="text-[11px] text-slate-500">
                Columns validated: email, password, passport_number, phone_number, birth_date, nationality.
              </div>

              <button
                type="button"
                onClick={handleValidatePreview}
                disabled={!file || uploading}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-500/20 transition-all disabled:opacity-50"
              >
                {uploading && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                Parse & Validate File
              </button>
            </div>
          </div>

          {/* Validation Preview Section */}
          {previewData && (
            <div className="space-y-5 animate-fade-in">
              
              {/* Summary Metrics */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
                  <div className="text-xs text-slate-400 font-medium mb-1">Total Rows Found</div>
                  <div className="text-2xl font-bold text-white">{previewData.total_rows}</div>
                </div>

                <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-center">
                  <div className="text-xs text-emerald-400 font-medium mb-1">Valid Rows (Ready)</div>
                  <div className="text-2xl font-bold text-emerald-400">{previewData.valid_count}</div>
                </div>

                <div className={`p-4 rounded-xl text-center border ${
                  previewData.invalid_count > 0 
                    ? 'bg-rose-950/20 border-rose-500/30' 
                    : 'bg-slate-900 border-slate-800'
                }`}>
                  <div className="text-xs text-slate-400 font-medium mb-1">Invalid Rows</div>
                  <div className={`text-2xl font-bold ${previewData.invalid_count > 0 ? 'text-rose-400' : 'text-slate-400'}`}>
                    {previewData.invalid_count}
                  </div>
                </div>
              </div>

              {/* Invalid Rows Table */}
              {previewData.invalid_rows?.length > 0 && (
                <div className="bg-slate-900/80 border border-rose-500/30 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center gap-2 text-rose-400 text-sm font-semibold">
                    <XCircle className="w-4 h-4" />
                    <span>Row Validation Issues ({previewData.invalid_rows.length})</span>
                  </div>
                  <p className="text-xs text-slate-300">
                    The following records contain missing or malformed fields and will not be imported:
                  </p>

                  <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950">
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="text-[11px] uppercase bg-slate-900 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="py-2.5 px-3 w-16 text-center">Row #</th>
                          <th className="py-2.5 px-3">Identifier / Email</th>
                          <th className="py-2.5 px-3">Passport</th>
                          <th className="py-2.5 px-3">Detected Errors</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/80">
                        {previewData.invalid_rows.map((inv, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/40">
                            <td className="py-2.5 px-3 text-center font-mono font-bold text-rose-400">
                              {inv.row_number}
                            </td>
                            <td className="py-2.5 px-3 font-mono text-slate-300">
                              {inv.email || '<Empty Email>'}
                            </td>
                            <td className="py-2.5 px-3 font-mono text-slate-300">
                              {inv.passport_number || '<Empty>'}
                            </td>
                            <td className="py-2.5 px-3">
                              <ul className="list-disc list-inside text-rose-400 space-y-0.5">
                                {inv.errors?.map((err, errIdx) => (
                                  <li key={errIdx}>{err}</li>
                                ))}
                              </ul>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Valid Rows Preview Table */}
              {previewData.valid_rows?.length > 0 && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Valid Records Preview ({previewData.valid_rows.length})</span>
                    </div>

                    <button
                      onClick={handleConfirmImport}
                      disabled={importing}
                      className="flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 shadow-md shadow-emerald-500/20 transition-all disabled:opacity-50"
                    >
                      {importing && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                      Confirm & Import Valid Records ({previewData.valid_rows.length})
                    </button>
                  </div>

                  <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950 max-h-72">
                    <table className="w-full text-left text-xs text-slate-300">
                      <thead className="text-[11px] uppercase bg-slate-900 text-slate-400 border-b border-slate-800 sticky top-0">
                        <tr>
                          <th className="py-2 px-3">Name</th>
                          <th className="py-2 px-3">Email</th>
                          <th className="py-2 px-3">Passport</th>
                          <th className="py-2 px-3">Nationality</th>
                          <th className="py-2 px-3">DOB</th>
                          <th className="py-2 px-3">Phone</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/80">
                        {previewData.valid_rows.slice(0, 50).map((vr, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/40">
                            <td className="py-2 px-3 text-white font-medium">{vr.full_name}</td>
                            <td className="py-2 px-3 text-slate-300">{vr.email}</td>
                            <td className="py-2 px-3 font-mono text-slate-200 font-semibold">{vr.passport_number}</td>
                            <td className="py-2 px-3 text-slate-300">{vr.nationality}</td>
                            <td className="py-2 px-3 text-slate-400">{vr.birth_date}</td>
                            <td className="py-2 px-3 text-slate-400">{vr.phone_number}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {previewData.valid_rows.length > 50 && (
                    <div className="text-[11px] text-slate-500 text-center">
                      Showing first 50 of {previewData.valid_rows.length} valid rows.
                    </div>
                  )}
                </div>
              )}

            </div>
          )}
        </>
      )}

    </div>
  );
};

export default ExcelImportPage;
