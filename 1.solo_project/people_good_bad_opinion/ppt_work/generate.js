const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');
const html2pptx = require('/Users/baeseungjae/Documents/GitHub/skills-main/skills/pptx/scripts/html2pptx.js');

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.title = '임성근 음주운전 논란 여론 분석';

    const slidesDir = '/Users/baeseungjae/Documents/GitHub/kdt_woongin/1.solo_project/people_good_bad_opinion/ppt_work/slides';
    const slideFiles = [
        'slide1.html', 'slide2.html', 'slide3.html', 'slide4.html', 'slide5.html',
        'slide6.html', 'slide7.html', 'slide8.html', 'slide9.html', 'slide10.html'
    ];

    for (let i = 0; i < slideFiles.length; i++) {
        const htmlFile = path.join(slidesDir, slideFiles[i]);
        console.log(`Processing ${slideFiles[i]}...`);
        const { slide, placeholders } = await html2pptx(htmlFile, pptx);

        // Add charts to placeholders
        if (slideFiles[i] === 'slide4.html') {
            const p = placeholders.find(pl => pl.id === 'donut-chart');
            if (p) {
                slide.addChart(pptx.charts.PIE, [
                    { name: '여론 분포', labels: ['긍정(지지)', '부정(분노/실망/조롱)', '그외'], values: [50.2, 37.5, 12.2] }
                ], {
                    x: p.x, y: p.y, w: p.w, h: p.h,
                    showPercent: true, showLegend: true, legendPos: 'b',
                    chartColors: ['00CC96', 'E33737', '636EFA']
                });
            }
        }

        if (slideFiles[i] === 'slide5.html') {
            const p = placeholders.find(pl => pl.id === 'compare-bar-chart');
            if (p) {
                slide.addChart(pptx.charts.BAR, [
                    { name: '논란 전', labels: ['지지', '분노', '중립', '실망', '조롱', '그외'], values: [50.6, 1.4, 22.4, 1.7, 14.9, 9.0] },
                    { name: '논란 후', labels: ['지지', '분노', '중립', '실망', '조롱', '그외'], values: [9.46, 15.0, 6.65, 9.31, 42.4, 17.1] }
                ], {
                    x: p.x, y: p.y, w: p.w, h: p.h,
                    barDir: 'col', showLegend: true, legendPos: 't',
                    chartColors: ['636EFA', 'E33737'],
                    showCatAxisTitle: false, showValAxisTitle: true, valAxisTitle: '비율 (%)'
                });
            }
        }

        if (slideFiles[i] === 'slide6.html') {
            const p = placeholders.find(pl => pl.id === 'comparison-chart');
            if (p) {
                slide.addChart(pptx.charts.BAR, [
                    { name: '임성근(논란후)', labels: ['조롱', '분노', '그외', '실망', '지지', '중립'], values: [42.4, 15.0, 17.1, 9.31, 9.46, 6.65] },
                    { name: '백종원', labels: ['조롱', '분노', '그외', '실망', '지지', '중립'], values: [38.0, 24.7, 14.0, 10.5, 7.14, 5.59] }
                ], {
                    x: p.x, y: p.y, w: p.w, h: p.h,
                    barDir: 'bar', showLegend: true, legendPos: 'r',
                    chartColors: ['E33737', '636EFA'],
                    valAxisTitle: '비율 (%)',
                    showValAxisTitle: true
                });
            }
        }

        if (slideFiles[i] === 'slide7.html') {
            const p1 = placeholders.find(pl => pl.id === 'timeseries-lim');
            if (p1) {
                slide.addChart(pptx.charts.LINE, [
                    { name: '부정 비율', labels: ['1/13', '1/14', '1/15', '1/16', '1/17', '1/18', '1/19', '1/20', '1/21', '1/22'], values: [0.0, 9.3, 4.8, 11.6, 7.9, 22.7, 72.2, 72.2, 67.0, 70.1] }
                ], {
                    x: p1.x, y: p1.y, w: p1.w, h: p1.h,
                    showLegend: false, chartColors: ['E33737'], lineSize: 3,
                    showValAxisTitle: true, valAxisTitle: '%'
                });
            }
            const p2 = placeholders.find(pl => pl.id === 'timeseries-baek');
            if (p2) {
                slide.addChart(pptx.charts.LINE, [
                    { name: '부정 비율', labels: ['25.04', '25.05', '25.06', '25.07', '25.08', '25.09', '25.10'], values: [85.1, 80.2, 57.0, 76.7, 51.7, 60.7, 46.0] }
                ], {
                    x: p2.x, y: p2.y, w: p2.w, h: p2.h,
                    showLegend: false, chartColors: ['636EFA'], lineSize: 3,
                    showValAxisTitle: true, valAxisTitle: '%'
                });
            }
        }

        if (slideFiles[i] === 'slide8.html') {
            const p = placeholders.find(pl => pl.id === 'trend-chart');
            if (p) {
                slide.addChart(pptx.charts.LINE, [
                    { name: '조회수(억)', labels: ['1/23', '1/26', '1/27', '1/28'], values: [3.72, 4.20, 4.13, 4.13] },
                    { name: '영상수', labels: ['1/23', '1/26', '1/27', '1/28'], values: [1605, 1690, 1677, 1655] }
                ], {
                    x: p.x, y: p.y, w: p.w, h: p.h,
                    showLegend: true, legendPos: 't', chartColors: ['F1C40F', '636EFA'],
                    lineSize: 2, catAxisOrientation: 'minMax',
                    valAxes: [
                        { showValAxisTitle: true, valAxisTitle: '조회수(억)', valGridLine: { style: 'none' } },
                        { showValAxisTitle: true, valAxisTitle: '영상수', valGridLine: { style: 'none' } }
                    ]
                });
            }
        }
    }

    const outputPath = '/Users/baeseungjae/Documents/GitHub/kdt_woongin/1.solo_project/people_good_bad_opinion/임성근_여론분석_결과보고서.pptx';
    await pptx.writeFile({ fileName: outputPath });
    console.log(`Presentation created: ${outputPath}`);
}

createPresentation().catch(err => {
    console.error(err);
    process.exit(1);
});
