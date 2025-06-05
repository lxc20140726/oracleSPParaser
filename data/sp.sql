CREATE OR REPLACE PROCEDURE sp_1(
    p_tgrcf VARCHAR2,
    p_tgrct VARCHAR2,
    p_prefix VARCHAR2,
    p_cde VARCHAR2,
    p_post VARCHAR2,
    p_ssss VARCHAR2,
    p_vvv VARCHAR2,
    p_yyy VARCHAR2,
    p_l VARCHAR2,
    p_num VARCHAR2,
    p_pl VARCHAR2,
    p_pod VARCHAR2,
    p_fnd NUMBER,
    p_por NUMBER,
    p_rst DATE,
    p_ret DATE,
    p_f_pol VARCHAR2,
    p_l_pod VARCHAR2,
    p_vnc VARCHAR2,
    p_vvv VARCHAR2,
    p_carrier VARCHAR2,
    p_port_loc VARCHAR2,
    p_boolc VARCHAR2,
    p_arr_dt_loc_from DATE,
    p_arr_dt_loc_to DATE,
    p_ddlf DATE,
    p_ddlt DATE,
    p_max_row NUMBER
) IS
    l_tgrcf VARCHAR2(38) := p_tgrcf;
    l_tgrct VARCHAR2(38) := p_tgrct;
    prefix  VARCHAR2(10) := p_prefix;
    cde     VARCHAR2(38) := p_cde;
    post    VARCHAR2(10) := p_post;
    ssss    VARCHAR2(4)  := p_ssss;
    vvv     VARCHAR2(5)  := p_vvv;
    yyy     VARCHAR2(4)  := p_yyy;
    l_d     VARCHAR2(25) := p_l;
    l_num   VARCHAR2(5)  := p_num;
    l_pl    VARCHAR2(35) := p_pl;
    l_rst   DATE         := p_rst;
    l_ret   DATE         := p_ret;
    l_vnc   VARCHAR2(3)  := p_vnc;
    l_vr    VARCHAR2(20) := p_vvv;
    l_boc   VARCHAR2(3)  := p_boolc;
    l_ddlf  DATE         := p_ddlf;
    l_ddlt  DATE         := p_ddlt;
BEGIN
    IF isnull(cde, '') IS NOT NULL THEN
        INSERT INTO table_1 (col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9, col_10, col_11, col_12, col_13, col_14, col_15, col_16)
        SELECT DISTINCT a.col_1,
                        a.col_2,
                        a.col_3,
                        a.col_4,
                        a.col_5,
                        a.col_6,
                        a.col_7,
                        a.col_8,
                        a.col_9,
                        a.col_10,
                        a.col_11,
                        a.col_12,
                        a.col_13,
                        a.col_14,
                        a.col_15,
                        a.col_16
        FROM table_2 a
        WHERE a.col_1 = cde
          AND (a.col_2 = prefix OR isnull(prefix, '') IS NULL)
          AND (a.col_3 = post OR isnull(post, '') IS NULL)
          AND (a.col_4 = l_pl OR l_pl IS NULL);
           INSERT INTO table_3 (col_1, col_2, col_3, col_4, col_5)
        SELECT DISTINCT c.col_1, a.col_2, a.col_3, a.col_4, a.col_5
        FROM table_4 a,
             table_5 c,
             table_6 d
        WHERE a.col_1 =
              rtrim(CASE WHEN prefix IS NULL THEN '' ELSE prefix END) ||
              rtrim(cde) ||
              rtrim(CASE WHEN post IS NULL THEN '' ELSE post END)
          AND a.col_2 = c.col_2
          AND a.col_3 = c.col_3
          AND c.col_4 = d.col_4
          AND c.col_5 = d.col_5
          AND (d.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
          AND (d.col_7 = p_pod OR isnull(p_pod, '') IS NULL)
          AND (d.col_8 = ssss OR isnull(ssss, '') IS NULL)
          AND (d.col_9 = vvv OR isnull(vvv, '') IS NULL)
          AND (d.col_10 = yyy OR isnull(yyy, '') IS NULL)
          AND (d.col_11 = l_d OR isnull(l_d, '') IS NULL)
          AND (c.col_12 = p_tgrcf OR isnull(p_tgrcf, '') IS NULL);
    ELSE
        IF isnull(p_tgrcf, '') IS NOT NULL AND isnull(l_tgrct, '') IS NOT NULL THEN
            INSERT INTO table_3 (col_1, col_2, col_3, col_4, col_5)
            SELECT DISTINCT c.col_1, a.col_2, a.col_3, a.col_4, a.col_5
            FROM table_4 a,
                 table_5 c,
                 table_6 d
            WHERE c.col_1 >= p_tgrcf
              AND c.col_1 <= l_tgrct
              AND a.col_2 = c.col_2
              AND a.col_3 = c.col_3
              AND c.col_4 = d.col_4
              AND c.col_5 = d.col_5
              AND (d.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
              AND (d.col_7 = p_pod OR isnull(p_pod, '') IS NULL)
              AND (d.col_8 = ssss OR isnull(ssss, '') IS NULL)
              AND (d.col_9 = vvv OR isnull(vvv, '') IS NULL)
              AND (d.col_10 = yyy OR isnull(yyy, '') IS NULL)
              AND (d.col_11 = l_d OR isnull(l_d, '') IS NULL);
        ELSIF isnull(p_tgrcf, '') IS NOT NULL AND isnull(l_tgrct, '') IS NOT NULL THEN
            INSERT INTO table_3 (col_1, col_2, col_3, col_4, col_5)
            SELECT DISTINCT c.col_1, a.col_2, a.col_3, a.col_4, a.col_5
            FROM table_4 a,
                 table_5 c,
                 table_6 d
            WHERE c.col_1 = p_tgrcf
              AND a.col_2 = c.col_2
              AND a.col_3 = c.col_3
              AND c.col_4 = d.col_4
              AND c.col_5 = d.col_5
              AND (d.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
              AND (d.col_7 = p_pod OR isnull(p_pod, '') IS NULL)
              AND (d.col_8 = ssss OR isnull(ssss, '') IS NULL)
              AND (d.col_9 = vvv OR isnull(vvv, '') IS NULL)
              AND (d.col_10 = yyy OR isnull(yyy, '') IS NULL)
              AND (d.col_11 = l_d OR isnull(l_d, '') IS NULL);
              ELSIF isnull(p_tgrcf, '') IS NULL AND isnull(l_tgrct, '') IS NOT NULL THEN
            INSERT INTO table_3 (col_1, col_2, col_3, col_4, col_5)
            SELECT DISTINCT c.col_1, a.col_2, a.col_3, a.col_4, a.col_5
            FROM table_4 a,
                 table_5 c,
                 table_6 d
            WHERE c.col_1 = l_tgrct
              AND a.col_2 = c.col_2
              AND a.col_3 = c.col_3
              AND c.col_4 = d.col_4
              AND c.col_5 = d.col_5
              AND (d.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
              AND (d.col_7 = p_pod OR isnull(p_pod, '') IS NULL)
              AND (d.col_8 = ssss OR isnull(ssss, '') IS NULL)
              AND (d.col_9 = vvv OR isnull(vvv, '') IS NULL)
              AND (d.col_10 = yyy OR isnull(yyy, '') IS NULL)
              AND (d.col_11 = l_d OR isnull(l_d, '') IS NULL);
        ELSIF isnull(ssss, '') IS NOT NULL THEN
            IF l_num = 'AL' THEN
                INSERT INTO table_3 (col_1, col_2, col_3)
                SELECT DISTINCT b.col_1, b.col_2, NULL
                FROM table_6 a,
                     table_5 b
                WHERE a.col_8 = ssss
                  AND a.col_9 = vvv
                  AND a.col_10 = yyy
                  AND a.col_11 = l_d
                  AND a.col_12 = b.col_12
                  AND a.col_2 = b.col_2
                  AND a.col_3 = b.col_3
                  AND (a.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
                  AND (a.col_7 = p_pod OR isnull(p_pod, '') IS NULL);

                UPDATE table_3 a
                SET (col_3, col_5) =
                        (SELECT b.col_3, b.col_5
                         FROM table_4 b
                         WHERE a.col_4 = b.col_4
                           AND rownum = 1)
                WHERE EXISTS (SELECT 1
                              FROM table_4 b
                              WHERE a.col_4 = b.col_4);
            END IF;
        ELSIF isnull(l_vnc, '') IS NOT NULL THEN
            INSERT INTO table_7
            SELECT DISTINCT b.col_1,
                            b.col_2,
                            b.col_3,
                            b.col_4,
                            b.col_5,
                            b.col_6,
                            b.col_7,
                            b.col_8
            FROM table_8 b
            WHERE b.col_9 = l_vnc
              AND upper(b.col_10) = l_vr
              AND b.col_11 = 'coastal';

            INSERT INTO table_3 (col_1, col_2, col_3)
            SELECT DISTINCT c.col_1, c.col_2, NULL
            FROM table_7 b,
                 table_6 a,
                 table_5 c
            WHERE a.col_1 = b.col_1
              AND a.col_2 = b.col_2
              AND a.col_3 = b.col_3
              AND a.col_4 = b.col_4
              AND a.col_5 = b.col_5
              AND a.col_6 = b.col_6
              AND a.col_7 = b.col_7
              AND a.col_12 = b.col_8
              AND a.col_2 = c.col_2
              AND a.col_3 = c.col_3
              AND (a.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
              AND (a.col_7 = p_pod OR isnull(p_pod, '') IS NULL);
               UPDATE table_3 a
            SET (col_3, col_5) =
                    (SELECT b.col_3, b.col_5
                     FROM table_4 b
                     WHERE a.col_4 = b.col_4
                       AND rownum = 1)
            WHERE EXISTS (SELECT 1
                          FROM table_4 b
                          WHERE a.col_4 = b.col_4);
        ELSIF isnull(l_ddlf, '') IS NOT NULL THEN
            INSERT INTO table_7
            SELECT DISTINCT b.col_1,
                            b.col_2,
                            b.col_3,
                            b.col_4,
                            b.col_5,
                            b.col_6,
                            b.col_7,
                            b.col_8
            FROM table_8 b
            WHERE b.col_8 >= l_ddlf
              AND b.col_8 <= l_ddlt
              AND b.col_11 = 'coastal';

            INSERT INTO table_3 (col_1, col_2, col_3)
            SELECT DISTINCT c.col_1, c.col_2, NULL
            FROM table_7 b,
                 table_6 a,
                 table_5 c
            WHERE a.col_1 = b.col_1
              AND a.col_2 = b.col_2
              AND a.col_3 = b.col_3
              AND a.col_4 = b.col_4
              AND a.col_5 = b.col_5
              AND a.col_6 = b.col_6
              AND a.col_7 = b.col_7
              AND a.col_12 = b.col_8
              AND a.col_2 = c.col_2
              AND a.col_3 = c.col_3
              AND (a.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
              AND (a.col_7 = p_pod OR isnull(p_pod, '') IS NULL);
               UPDATE table_3 a
            SET (col_3, col_5) =
                    (SELECT b.col_3, b.col_5
                     FROM table_4 b
                     WHERE a.col_4 = b.col_4
                       AND rownum = 1)
            WHERE EXISTS (SELECT 1
                          FROM table_4 b
                          WHERE a.col_4 = b.col_4);
        ELSIF l_boc IS NOT NULL THEN
            INSERT INTO table_3 (col_1, col_2, col_3, col_4, col_5)
            SELECT DISTINCT c.col_1, a.col_2, a.col_3, a.col_4, a.col_5
            FROM table_4 a,
                 table_5 c,
                 table_6 d
            WHERE a.col_5 = l_boc
              AND a.col_2 = c.col_2
              AND a.col_3 = c.col_3
              AND c.col_4 = d.col_4
              AND c.col_5 = d.col_5
              AND (d.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
              AND (d.col_7 = p_pod OR isnull(p_pod, '') IS NULL)
              AND (d.col_8 = ssss OR isnull(ssss, '') IS NULL)
              AND (d.col_9 = vvv OR isnull(vvv, '') IS NULL)
              AND (d.col_10 = yyy OR isnull(yyy, '') IS NULL)
              AND (d.col_11 = l_d OR isnull(l_d, '') IS NULL);
        ELSIF (isnull(l_rst, '') IS NOT NULL AND isnull(l_ret, '') IS NOT NULL AND
               (isnull(l_pl, '') IS NOT NULL OR isnull(p_pod, '') IS NOT NULL)) THEN
            INSERT INTO table_1
            SELECT DISTINCT a.col_1,
                            a.col_2,
                            a.col_3,
                            a.col_4,
                            a.col_5,
                            a.col_6,
                            a.col_7,
                            a.col_8,
                            a.col_9,
                            a.col_10,
                            a.col_11,
                            a.col_12,
                            a.col_13,
                            a.col_14,
                            a.col_15,
                            a.col_16
            FROM table_2 a
            WHERE a.col_14 >= l_rst
              AND a.col_14 < l_ret
              AND a.col_11 = l_pl;

            INSERT INTO table_3 (col_1, col_2, col_3, col_4, col_5)
            SELECT DISTINCT c.col_1, a.col_2, a.col_3, a.col_4, a.col_5
            FROM table_1 e,
                 table_4 a,
                 table_5 c,
                 table_6 d
            WHERE e.col_4 = a.col_2
              AND a.col_2 = c.col_2
              AND a.col_3 = c.col_3
              AND c.col_4 = d.col_4
              AND c.col_5 = d.col_5
              AND (d.col_6 = l_pl OR isnull(l_pl, '') IS NULL)
              AND (d.col_7 = p_pod OR isnull(p_pod, '') IS NULL)
              AND (d.col_8 = ssss OR isnull(ssss, '') IS NULL)
              AND (d.col_9 = vvv OR isnull(vvv, '') IS NULL)
              AND (d.col_10 = yyy OR isnull(yyy, '') IS NULL)
              AND (d.col_11 = l_d OR isnull(l_d, '') IS NULL);
        END IF;
    END IF;

END sp_1;